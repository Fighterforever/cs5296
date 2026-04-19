# Troubleshooting notes

A running list of issues we hit while setting the project up and how we
resolved them. Useful for anyone re-running the benchmark matrix or
adapting the Terraform for another workload.

## Lambda concurrency quota on a fresh AWS account

**Symptom.** `tofu apply` fails with
`InvalidParameterValueException: Specified ReservedConcurrentExecutions
for function decreases account's UnreservedConcurrentExecution below its
minimum value of 10.`

**Cause.** Brand-new AWS accounts ship with a default account-wide
Lambda concurrency limit of 10. Setting any `reserved_concurrent_executions`
on the function tries to take capacity away from the unreserved pool
below that floor.

**Fix.** Either raise the quota via the Service Quotas console
("Concurrent executions") and wait for approval, or set
`lambda_reserved_concurrency = -1` in `terraform.tfvars` (no reservation,
safe for measured rates below ~300 RPS).

## ECS task role doesn't include DynamoDB permissions

**Symptom.** Fargate task starts and ALB health-check passes, but
`POST /shorten` returns 500 and the CloudWatch log shows
`botocore.exceptions.ClientError: AccessDeniedException`.

**Cause.** Fargate distinguishes *execution role* (pulling the image,
writing logs) from *task role* (what the container itself can do). We
originally attached only the execution role's DynamoDB policy.

**Fix.** `infra/modules/shared/iam.tf` now creates a separate
`cs5296-ecs-task-role` with `AmazonDynamoDBFullAccess`, and
`infra/modules/fargate/main.tf` assigns that role as `task_role_arn`
(distinct from `execution_role_arn`).

## Benchmark run fails to upload results to S3

**Symptom.** The load-generator EC2 finishes `bash benchmark/run.sh` but
`aws s3 sync` errors with `User ... is not authorized to perform:
s3:ListBucket`.

**Cause.** The EC2 instance profile on the load-gen had only
`AmazonEC2ContainerRegistryReadOnly + AmazonDynamoDBFullAccess +
AmazonSSMManagedInstanceCore`. It was missing S3 access.

**Fix.** Attach an inline IAM policy allowing
`s3:ListBucket / GetObject / PutObject` on the specific result bucket
before the sync step. We do this in-line rather than broadly granting
`AmazonS3FullAccess` to keep the principle of least privilege.

## ALB health check returns 404 on path-prefixed routes

**Symptom.** `curl http://<alb>/ec2/healthz` returns 404; the FastAPI
application itself works on `http://localhost:8080/healthz`.

**Cause.** ALB listener rules forward requests without rewriting the
path, so the EC2 / Fargate / Lambda container all see the prefix
(`/ec2`, `/fargate`, `/lambda`) and reject it.

**Fix.** `app/src/main.py` installs a tiny ASGI middleware that strips
the `PATH_PREFIX` environment variable from incoming requests. Each
deployment passes its own prefix as env (`PATH_PREFIX=/ec2` on EC2,
`/fargate` on Fargate, `/lambda` on Lambda). The same container image
works on all three.

## k6 reports "body is null" under high RPS

**Symptom.** At 400+ RPS, k6 logs thousands of
`GoError: the body is null` warnings inside `doShorten`.

**Cause.** k6's `discardResponseBodies: true` option drops the body
before user code can read it. Setting `responseType: 'text'` per-request
retains the body for JSON parsing.

**Fix.** `benchmark/lib/common.js` wraps the POST call with a
try/catch that throws only when the response body is genuinely empty
(not when k6 discarded it).

## tofu destroy leaves orphan network interfaces

**Symptom.** After `tofu destroy`, the VPC dashboard still shows
"available" ENIs tagged with `cs5296-*` and the delete fails with
`DependencyViolation`.

**Cause.** Fargate tasks and Lambda ENIs sometimes detach slowly; by
the time Terraform finishes destroying dependents, the ENIs appear
"available" but belong to deleted resources.

**Fix.** `make nuke` in the top-level Makefile runs `tofu destroy`
first, then sweeps available ENIs and unattached EIPs tagged with our
project prefix. Always run `make nuke` rather than `tofu destroy` alone
at tear-down.

## AWS Academy Learner Lab deactivation

**Symptom.** `Start Lab` button is red; the info panel says
`AWS account deactivated at <timestamp>`.

**Cause.** Running sustained Lambda-heavy workloads (including a
cold-start probe with many fresh container inits) for multiple hours
can trigger the Vocareum automated abuse-detection layer. Traffic
volume in our case was well under AWS's commercial thresholds (8 Mbps
against a 1 Gbps limit), but Learner Lab has stricter tenant-level
heuristics.

**Fix.** None at our level — Vocareum deactivation requires course
administrator intervention. We migrated to a personal AWS account with
three substitutions (self-managed IAM roles, no public Lambda Function
URLs, no reserved Lambda concurrency) and re-ran the matrix from a
fresh account.
