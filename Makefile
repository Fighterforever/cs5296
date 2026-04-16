SHELL := /bin/bash
.DEFAULT_GOAL := help

REGION ?= us-east-1
STACK  ?= infra/envs/benchmark
IMAGE  ?= shortlink:dev

## help: show targets
help:
	@awk -F ':.*##' '/^[a-zA-Z_-]+:.*##/ {printf "  %-12s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

## image: build the multi-arch container image
image: ## build the container image (linux/amd64 by default)
	docker buildx build --platform linux/amd64 -t $(IMAGE) -f app/Dockerfile app

## up: terraform apply the whole stack
up:
	cd $(STACK) && terraform init -input=false && terraform apply -auto-approve

## down: destroy everything
down:
	cd $(STACK) && terraform destroy -auto-approve

## bench: run the k6 benchmark matrix against the deployed endpoints
bench:
	bash benchmark/run.sh

## analyze: post-process raw k6 output into figures + tables
analyze:
	python -m analysis.build_figures

## report: compile the LaTeX report
report:
	$(MAKE) -C report

## clean: wipe generated artefacts (not terraform state)
clean:
	rm -rf data/results/*.json data/results/*.csv report/build report/main.pdf

.PHONY: help image up down bench analyze report clean
