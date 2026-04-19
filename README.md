# Comparative Analysis of Web Service Deployment Paradigms on AWS

CS5296 Cloud Computing, Spring 2026 — Group project.

We deploy the same stateless web service (a URL shortener backed by DynamoDB) on
three AWS compute paradigms — **EC2** (virtual machines, Auto Scaling), **ECS
Fargate** (managed containers), and **Lambda** (serverless functions) — and run
a controlled benchmark to compare them on four axes:

1. Steady-state throughput and tail latency (p50/p95/p99) under increasing
   offered RPS.
2. Elasticity: time-to-steady-state under step-arrival bursts.
3. Lambda warm-retention probe at fixed 1 GB / no reserved concurrency.
   A full memory-sweep plus provisioned-concurrency study is flagged as
   future work in the report's *Threats to Validity* section.
4. Cost per million requests and the break-even points between the three
   paradigms, using a compute-only model that excludes shared costs
   (ALB, DynamoDB) so they cancel across the three paradigms.

The whole stack is reproducible: Terraform for infrastructure, a single
container image (Lambda Web Adapter fronts the same FastAPI app on all three
runtimes), `k6` for load, and a Python pipeline for analysis.

## Repository layout

```
app/          FastAPI short-link service + Dockerfile
infra/        Terraform (modules/shared, ec2, fargate, lambda)
benchmark/    k6 scenarios (steady / burst / cold-start / mixed)
analysis/     Python post-processing, figure generation
report/       LaTeX source of the final report
docs/         architecture notes, demo script
data/         raw benchmark output (git-ignored)
```

## Quick start

```bash
# prereqs: docker, opentofu (or terraform), aws cli v2, python 3.12, k6 v1
export AWS_PROFILE=<your-profile>

make up        # tofu apply: 39 AWS resources in ~7 min
make image     # docker buildx + push shared container image to ECR
make bench     # k6 matrix: steady / burst / cold-start / mixed (~60 min)
make analyze   # regenerate 5 figures + 4 summary CSVs from raw k6 output
make report    # compile LaTeX report PDF
make nuke      # tofu destroy + sweep orphan ENIs/EIPs
```

Typical end-to-end AWS spend for one full matrix run: **under USD 5**.

Detailed instructions live in `docs/` and in the Artifact Appendix of the
report (`report/main.pdf`).

## Authors

- Ma Liyu (liyuma2, 59072966)
- Zheng Junlan (junlzheng4, 59507980)
- Zheng Zelan (zelazheng2, 59250714)
