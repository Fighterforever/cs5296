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
	cd $(STACK) && tofu init -input=false && tofu apply -auto-approve

## down: destroy everything
down:
	cd $(STACK) && tofu destroy -auto-approve

## nuke: destroy + sweep common leftovers (stray ENIs, unattached EIPs) — idempotent
nuke:
	-cd $(STACK) && tofu destroy -auto-approve
	@echo "== sweeping unattached EIPs =="
	-aws --region $(REGION) ec2 describe-addresses \
	  --query "Addresses[?AssociationId==null].AllocationId" --output text \
	  | xargs -r -n1 aws --region $(REGION) ec2 release-address --allocation-id
	@echo "== sweeping detached ENIs with cs5296 tag =="
	-aws --region $(REGION) ec2 describe-network-interfaces \
	  --filters Name=status,Values=available Name=tag:Name,Values=cs5296* \
	  --query "NetworkInterfaces[].NetworkInterfaceId" --output text \
	  | xargs -r -n1 aws --region $(REGION) ec2 delete-network-interface --network-interface-id
	@echo "== done. re-check console to confirm zero residuals =="

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

.PHONY: help image up down nuke bench analyze report clean
