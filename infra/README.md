# Infrastructure (Terraform)

This stack provisions three equivalent deployments of the same container image
on AWS: EC2 behind an ALB + Auto Scaling, ECS Fargate behind an ALB, and Lambda
(container image, Function URL, also optionally fronted by the shared ALB for a
fair comparison).

## Design for the Vocareum Learner Lab

The Learner Lab sandbox does **not** allow IAM role creation. Every module
therefore references the pre-existing `LabRole` by ARN (see
`modules/shared/iam.tf`). The default VPC and its subnets are reused rather
than created.

## Layout

```
modules/
  shared/      VPC lookup, SGs, ECR repo, DynamoDB table, ALB + two listener rules
  ec2/         launch template, target group, ASG with target tracking
  fargate/     ECS cluster, task def, service, app autoscaling
  lambda/      container-image function, Function URL, ALB attachment
envs/
  benchmark/   the "one environment" that wires the four modules together
```

## Quick usage

```bash
cd infra/envs/benchmark
terraform init
terraform apply -var="account_id=$(aws sts get-caller-identity --query Account --output text)"
# endpoints are printed at the end: ec2_url / fargate_url / lambda_url / lambda_alb_url
terraform destroy
```

## Budget control

The ALB (a persistent cost of ~$0.0225/h) is the largest fixed cost. Teardown
is instant; running the whole stack for 8 hours costs under $1.
