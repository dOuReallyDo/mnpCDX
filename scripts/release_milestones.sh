#!/usr/bin/env bash
set -euo pipefail

git tag -a v0.1.0 -m "Foundation release"
git tag -a v0.2.0 -m "Analytics and API release"
git tag -a v0.3.0-mvp -m "Business MVP release"

echo "Tags created: v0.1.0, v0.2.0, v0.3.0-mvp"
