#!/bin/bash
# =============================================================================
# RV AI Skills Hub — Bootstrap Script
#
# Run this once after cloning on any machine. It:
#   1. Creates the local directory structure (no network needed).
#   2. Syncs all core/ skills to ~/.codex/AGENTS.md for global Codex access.
#   3. Attempts to clone vendor repositories (fails gracefully per vendor).
# =============================================================================

SUCCEEDED=()
FAILED=()

# ── Step 1: Directory structure ───────────────────────────────────────────────
echo ""
echo "── Creating directory structure ─────────────────────────────────────────"
mkdir -p core
mkdir -p .vendor
mkdir -p external/anthropic
mkdir -p external/huggingface
mkdir -p external/vercel
mkdir -p external/openai
echo "Done."

# ── Step 2: Global Codex setup ────────────────────────────────────────────────
# This is the key step for cross-machine skill discovery.
# It writes all skills from core/ into ~/.codex/AGENTS.md once,
# making them available in every Codex session on this machine.
echo ""
echo "── Syncing core skills to Codex global instructions ─────────────────────"
python3 adapters/skill_loader.py --sync-all

# ── Step 3: Vendor repositories ───────────────────────────────────────────────
declare -A VENDORS
VENDORS["anthropic"]="https://github.com/anthropics/skills.git"
VENDORS["huggingface"]="https://github.com/huggingface/skills.git"
VENDORS["vercel"]="https://github.com/vercel-labs/agent-skills.git"
VENDORS["openai"]="https://github.com/openai/skills.git"

echo ""
echo "── Syncing vendor repositories ──────────────────────────────────────────"

sync_vendor() {
    local name=$1
    local url=$2
    local dest=".vendor/$name"

    if [ -d "$dest/.git" ]; then
        echo "  Updating $name..."
        if (cd "$dest" && git pull --quiet); then
            echo "  ✓ $name updated."
            SUCCEEDED+=("$name")
        else
            echo "  ✗ $name — pull failed."
            FAILED+=("$name")
        fi
    else
        echo "  Cloning $name..."
        if git clone --depth 1 --quiet "$url" "$dest"; then
            echo "  ✓ $name cloned."
            SUCCEEDED+=("$name")
        else
            echo "  ✗ $name — clone failed. URL may not be a public repository."
            FAILED+=("$name")
        fi
    fi
}

for vendor in "${!VENDORS[@]}"; do
    sync_vendor "$vendor" "${VENDORS[$vendor]}"
done

# ── Summary ───────────────────────────────────────────────────────────────────
echo ""
echo "── Summary ──────────────────────────────────────────────────────────────"
[ ${#SUCCEEDED[@]} -gt 0 ] && echo "  Vendors synced:  ${SUCCEEDED[*]}"
[ ${#FAILED[@]}    -gt 0 ] && echo "  Vendors failed:  ${FAILED[*]}"
echo ""
echo "  Core skills are ready for Codex on this machine."
echo "  To add a new skill later, add it to core/ and re-run:"
echo "    python3 adapters/skill_loader.py --sync-all"
echo ""
