#!/bin/bash

# RV AI Skills Hub - Bootstrap Script
# This script populates the .vendor directory and ensures symlinks are valid.

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

mkdir -p .vendor

# Function to clone or update a repository
sync_repo() {
    local url=$1
    local dest=$2
    if [ -d ".vendor/$dest" ]; then
        echo "Updating $dest..."
        git -C ".vendor/$dest" pull --ff-only
    else
        echo "Cloning $dest..."
        git clone --depth 1 "$url" ".vendor/$dest"
    fi
}

echo "Starting vendor synchronization..."

sync_repo "git@github.com:anthropics/skills.git" "anthropic"
sync_repo "git@github.com:huggingface/skills.git" "huggingface"
sync_repo "git@github.com:vercel-labs/agent-skills.git" "vercel"
sync_repo "git@github.com:openai/skills.git" "openai"

echo "
Done! Your symlinks in /external are now valid."
echo "Run 'gemini skills link' on your vendor folders to register them."
