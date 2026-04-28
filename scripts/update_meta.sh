#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
OUTPUT_DIR="$PROJECT_DIR/output"
VENV="$PROJECT_DIR/.venv/bin/metatft-crawler"

cd "$PROJECT_DIR"

# Ensure venv is installed
if [[ ! -f "$VENV" ]]; then
    echo "ERROR: venv not found. Run: python3 -m venv .venv && .venv/bin/pip install -e . && .venv/bin/playwright install chromium"
    exit 1
fi

mkdir -p "$OUTPUT_DIR"

run_crawler() {
    local name="$1"
    local file="$OUTPUT_DIR/$2"
    echo ""
    echo ">>> Running $name crawler..."
    "$VENV" "$name" --format json --output "$file"
    echo "    Saved to $file"
}

run_crawler comps        comps.json
run_crawler units        units.json
run_crawler items        items.json
run_crawler augments     augments.json
run_crawler traits       traits.json
run_crawler comp-details comp_details.json

echo ""
echo ">>> Committing and pushing output files to GitHub..."
git add output/*.json
git diff --cached --quiet && echo "No changes to push." && exit 0

TIMESTAMP=$(date +"%Y-%m-%d %H:%M")
git commit -m "[data] Update meta data ($TIMESTAMP)"
git push origin main

echo ""
echo "Done. All meta files updated and pushed to GitHub."
