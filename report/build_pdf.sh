#!/usr/bin/env bash
# Build report.pdf from the single consolidated source.
#
# Requirements: pandoc, tectonic (both available via `brew install`).
# Uses macOS-bundled fonts: Arial Unicode MS for body, Menlo for code.
#
# Run from anywhere; paths are resolved relative to this script.

set -euo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

cd "$REPO_ROOT"

pandoc \
    report/report.md \
    -o report.pdf \
    --pdf-engine=tectonic \
    --resource-path=report

# Refresh Spotlight metadata so mdls returns the fresh page count (mdls
# otherwise reads its cached index from the previous build).
mdimport -t report.pdf 2>/dev/null || true
echo "Wrote $(pwd)/report.pdf ($(mdls -name kMDItemNumberOfPages -raw report.pdf 2>/dev/null || echo '?') pages)"
