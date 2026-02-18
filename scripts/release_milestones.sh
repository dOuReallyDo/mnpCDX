#!/usr/bin/env bash
set -euo pipefail

# Creates the progressive milestone tags for the mnpCDX Next program.
# Existing tags are skipped.

create_tag_if_missing() {
  local tag="$1"
  local msg="$2"
  if git rev-parse "$tag" >/dev/null 2>&1; then
    echo "skip: $tag already exists"
  else
    git tag -a "$tag" -m "$msg"
    echo "created: $tag"
  fi
}

create_tag_if_missing "v0.5.0" "Portfolio Convergence Baseline"
create_tag_if_missing "v0.6.0" "Data Reliability Core"
create_tag_if_missing "v0.7.0" "Analytics and Simulation Core"
create_tag_if_missing "v0.8.0" "Operations and Security Hardening"
create_tag_if_missing "v0.9.0-rc1" "Pilot Readiness Candidate"
create_tag_if_missing "v1.0.0-mvp" "First Business MVP"

echo "Done: progressive milestone tags configured"
