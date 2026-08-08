SHELL := /bin/bash
PY := .venv/bin/python
PIP := .venv/bin/pip
WORKSPACE ?= data/archive/workspace
CLI := $(PY) -m src.pipeline.cli
MSG ?=

.PHONY: bootstrap check-prereqs commit-spec commit-plan commit-slice commit-milestone \
	accept publish values trees runpod-infer pmtiles-buildings pmtiles-trees check-or005 \
	check-public check-history

## Setup ------------------------------------------------------------------

bootstrap: ## create venv, install deps, run acceptance suite once
	@bash scripts/check-prereqs.sh
	@git rev-parse --verify --quiet refs/heads/main >/dev/null \
		|| { echo "error: checkout branch main first"; exit 1; }
	python3.11 -m venv .venv
	$(PIP) install --quiet -e ".[dev]"
	@echo "== running acceptance suite =="
	-$(PY) -m pytest tests/acceptance -q
	@echo "bootstrap done"

check-prereqs: ## Python 3.11, tippecanoe >= 2.x, mannheim workspace readable
	@bash scripts/check-prereqs.sh

check-public: ## FR-010 gate: no personal paths/credentials in tracked files
	@bash scripts/check-public.sh

check-history: ## FR-001 gate: full git-history secret scan (feature 015)
	@bash scripts/check-git-history.sh

## Commit discipline (OR-004 / R-013) --------------------------------------

define require_msg
	@test -n "$(MSG)" || { echo "error: pass MSG=\"commit message\""; exit 1; }
endef

commit-spec: ## one commit per accepted specification
	$(call require_msg)
	@bash scripts/commit-check.sh Spec
	git add specs/ && git commit -m "$(MSG)" -m "Spec-$$(bash scripts/next-tag.sh Spec)"

commit-plan: ## one commit per accepted plan
	$(call require_msg)
	@bash scripts/commit-check.sh Plan
	git add specs/ && git commit -m "$(MSG)" -m "Plan-$$(bash scripts/next-tag.sh Plan)"

commit-slice: ## one commit per implementation slice
	$(call require_msg)
	@bash scripts/commit-check.sh Slice
	git add -A && git commit -m "$(MSG)" -m "Slice-$$(bash scripts/next-tag.sh Slice)"

commit-milestone: ## one commit per validation milestone
	$(call require_msg)
	@bash scripts/commit-check.sh Milestone
	git add -A && git commit -m "$(MSG)" -m "Milestone-$$(bash scripts/next-tag.sh Milestone)"

## Pipeline subcommands (contracts/cli.md) ----------------------------------

accept: ## re-validate every artifact in artifacts.manifest.json
	$(CLI) accept

publish: ## emit dist/ static bundle (refuses on pending/fail required inputs)
	$(CLI) publish

values: ## compute per-building 60 m values from accepted canopy mask
	$(CLI) values

trees: ## polygonize accepted canopy mask to trees_polygons.geojson
	$(CLI) trees

runpod-infer: ## gated: refuses unless MANNHEIM_RUNPOD_ENDPOINT is set
	$(CLI) runpod-infer

## PMTiles recipes (contracts/pmtiles-sources.md) ---------------------------

pmtiles-buildings:
	@test -f "$(WORKSPACE)/buildings.geojson" || { echo "error: $(WORKSPACE)/buildings.geojson missing (run values)"; exit 1; }
	tippecanoe --name buildings --layer buildings --minimum-zoom 10 --maximum-zoom 18 \
		--base-zoom 14 --drop-densest-as-needed --extend-zooms-if-still-dropping \
		--simplification 10 --simplify-only-low-zooms \
		--read-parallel --force --output="$(WORKSPACE)/buildings.pmtiles" "$(WORKSPACE)/buildings.geojson"

pmtiles-trees:
	@test -f "$(WORKSPACE)/trees_polygons.geojson" || { echo "error: $(WORKSPACE)/trees_polygons.geojson missing (run trees)"; exit 1; }
	tippecanoe --name trees --layer trees --minimum-zoom 10 --maximum-zoom 18 \
		--base-zoom 14 --drop-densest-as-needed --extend-zooms-if-still-dropping \
		--read-parallel --force --output="$(WORKSPACE)/trees.pmtiles" "$(WORKSPACE)/trees_polygons.geojson"

## Governance (OR-005) ------------------------------------------------------

check-or005: ## no *.tif / *.pmtiles / >50 MiB *.geojson tracked; excluded files recorded in manifest
	@$(PY) scripts/check_or005.py "$(WORKSPACE)"
