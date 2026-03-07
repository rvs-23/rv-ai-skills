# RV AI Skills Hub

This repository is a centralized "portable brain" for AI instructions and procedural workflows. It allows you to maintain a single source of truth for coding standards, data processing rules, and vendor expertise. It ensures consistency across Gemini, Claude Code, and Codex-based environments.

---

## Getting Started

1. **Clone**: `git clone git@github.com:rvs-23/rv-ai-skills.git`
2. **Setup**: `sh setup.sh` (Populates the hidden ".vendor/" directory).
3. **Integrate**: See the "Multi-Agent Integration" section.

---

## Multi-Agent Integration

Use these commands to bridge the Hub with different AI agents. 

### 1. Gemini CLI
Link each vendor folder individually:
- `gemini skills link /path/to/rv-ai-skills/external/anthropic`
- `gemini skills link /path/to/rv-ai-skills/external/vercel`
- `gemini skills link /path/to/rv-ai-skills/external/openai`
- `gemini skills link /path/to/rv-ai-skills/external/huggingface`
- Run `/memory refresh` to re-index.

### 2. Claude Code
Append skill logic to `CLAUDE.md`:
```bash
python3 adapters/skill_loader.py external/anthropic/git-flow claude /path/to/project
```

### 3. Codex CLI & Other Agents
Inject skills as rules or system prompts. Codex CLI is a terminal-based coding agent by OpenAI; it reads from `AGENTS.md` in the project root.
```bash
# For Cursor rules
python3 adapters/skill_loader.py core/writing_good_readme.md cursor /path/to/project

# For Codex CLI (AGENTS.md)
python3 adapters/skill_loader.py core/writing_good_readme.md codex /path/to/project

# For OpenAI system prompts
python3 adapters/skill_loader.py core/writing_good_readme.md openai .
```

---

## External Skill Sourcing

Import expertise from major vendors by linking from the ".vendor/" directory.

### 1. Sync All Vendors
```bash
cd .vendor/anthropic && git pull
```

### 2. Link a Specific Skill
```bash
cd external/anthropic && ln -s ../../.vendor/anthropic/skills/git-flow git-flow
```

---

## FAQ: Symlinks and Portability

### What is a Symlink and why use it?
A symbolic link is a "shortcut" to another file. We use **relative symlinks** so the hub remains functional even if moved. The `setup.sh` script ensures these links find their targets in ".vendor/".
