#!/bin/bash

# RV AI Skills Hub - Bootstrap Script
set -e

mkdir -p .vendor

sync_repo() {
    local url=$1
    local dest=$2
    if [ -d ".vendor/$dest" ]; then
        echo "Updating $dest..."
        cd ".vendor/$dest" && git pull && cd ../..
    else
        echo "Cloning $dest..."
        git clone --depth 1 "$url" ".vendor/$dest"
    fi
}

echo "Starting vendor synchronization..."

sync_repo "https://github.com/anthropics/skills.git" "anthropic"
sync_repo "https://github.com/huggingface/skills.git" "huggingface"
sync_repo "https://github.com/vercel-labs/agent-skills.git" "vercel"
sync_repo "https://github.com/openai/skills.git" "openai"

echo "Done!"
