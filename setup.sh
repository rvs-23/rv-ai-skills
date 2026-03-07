#!/bin/bash
# =============================================================================
# RV AI Skills Hub — Bootstrap Script
#
# What this script does:
#   1. Creates the required local directory structure (always succeeds).
#   2. Attempts to clone or update each vendor's skill repository.
#   3. Reports a clear summary of what worked and what failed.
#
# It deliberately does NOT use "set -e" — each vendor is tried independently
# so one failure doesn't abort the whole setup.
# =============================================================================

# Track results for the summary at the end
SUCCEEDED=()
FAILED=()

# ── Step 1: Scaffold local directories ───────────────────────────────────────
# These are created unconditionally — no network required.
# "core/" is where your personal skills live.
# "external/" is where symlinks to vendor skills live.
# ".vendor/" is where the actual vendor git clones live (hidden from git).

echo ""
echo "── Creating directory structure ─────────────────────────────────────────"
mkdir -p core
mkdir -p .vendor
mkdir -p external/anthropic
mkdir -p external/huggingface
mkdir -p external/vercel
mkdir -p external/openai
echo "Done. Directories are ready."

# ── Step 2: Define vendor sources ────────────────────────────────────────────
# Update these URLs when you find the verified public clone URLs for each
# vendor's skills repository. The ones below are the best guesses based on
# the organisations' GitHub presence, but verify them before relying on them.
#
# To check a URL: paste it into your browser. If it shows a GitHub repo, it's valid.

declare -A VENDORS
VENDORS["anthropic"]="https://github.com/anthropics/skills.git"
VENDORS["huggingface"]="https://github.com/huggingface/skills.git"
VENDORS["vercel"]="https://github.com/vercel-labs/agent-skills.git"
VENDORS["openai"]="https://github.com/openai/skills.git"

# ── Step 3: Clone or update each vendor ──────────────────────────────────────
echo ""
echo "── Syncing vendor repositories ──────────────────────────────────────────"

sync_vendor() {
    local name=$1
    local url=$2
    local dest=".vendor/$name"

    if [ -d "$dest/.git" ]; then
        # Repository already cloned — just pull latest changes
        echo "  Updating $name..."
        if (cd "$dest" && git pull --quiet); then
            echo "  ✓ $name updated."
            SUCCEEDED+=("$name")
        else
            echo "  ✗ $name — git pull failed. The repo may have moved."
            FAILED+=("$name")
        fi
    else
        # First time — do a shallow clone (faster, no full history needed)
        echo "  Cloning $name from $url..."
        if git clone --depth 1 --quiet "$url" "$dest"; then
            echo "  ✓ $name cloned."
            SUCCEEDED+=("$name")
        else
            echo "  ✗ $name — clone failed. URL may not be a public repository."
            echo "    Tried: $url"
            FAILED+=("$name")
        fi
    fi
}

# Call sync for each vendor — failures here do not stop the loop
for vendor in "${!VENDORS[@]}"; do
    sync_vendor "$vendor" "${VENDORS[$vendor]}"
done

# ── Step 4: Summary ───────────────────────────────────────────────────────────
echo ""
echo "── Summary ──────────────────────────────────────────────────────────────"

if [ ${#SUCCEEDED[@]} -gt 0 ]; then
    echo "  Succeeded: ${SUCCEEDED[*]}"
fi

if [ ${#FAILED[@]} -gt 0 ]; then
    echo "  Failed:    ${FAILED[*]}"
    echo ""
    echo "  For failed vendors, find the correct public HTTPS clone URL and"
    echo "  either update the VENDORS map in this script, or clone manually:"
    echo "    git clone --depth 1 <url> .vendor/<vendor-name>"
fi

echo ""
echo "  Local structure is ready regardless of vendor sync results."
echo "  Run 'sh verify.sh' to check symlinks and file integrity."
echo ""
