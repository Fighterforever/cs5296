# Comparative Analysis of Web Service Deployment Paradigms on AWS

CS5296 Cloud Computing, Spring 2026 — Group project.

We deploy the same stateless web service (a URL shortener backed by DynamoDB) on
three AWS compute paradigms — **EC2** (virtual machines, Auto Scaling), **ECS
Fargate** (managed containers), and **Lambda** (serverless functions) — and run
a controlled benchmark to compare them on four axes:

1. Steady-state throughput and tail latency (p50/p95/p99) under increasing
   concurrency.
2. Elasticity: time-to-steady-state under step-arrival bursts.
3. Cold-start behaviour for Lambda across memory sizes, with and without
   provisioned concurrency.
4. Cost per million requests and the break-even points between the three
   paradigms.

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
# build + push image, deploy all three stacks, run the benchmark, render figures
make up        # provision
make bench     # load test
make analyze   # generate figures
make report    # build PDF
make down      # tear everything down
```

Detailed instructions live in `docs/` and in the Artifact Appendix of the
report (`report/main.pdf`).

## Authors

- Ma Liyu (liyuma2, 59072966)
- Zheng Junlan (junlzheng4, 59507980)
- Zheng Zelan (zelazheng2, 59250714)
