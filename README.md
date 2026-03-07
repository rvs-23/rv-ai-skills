# RV AI Skills Hub

This repository is a centralized "portable brain" that stores high-fidelity instructions and procedural workflows for AI agents. It allows you to maintain a single source of truth for your coding standards, data processing rules, and vendor-provided expertise. By using a linked architecture, it ensures that your AI tools—whether Gemini, Claude, or Codex-based terminal agents—always behave with the same level of precision and consistency across different machines.

---

## Getting Started

1. Clone the hub:
```bash
git clone git@github.com:rvs-23/rv-ai-skills.git
```
2. Run setup from the repo root (populates `.vendor/`):
```bash
sh setup.sh
```
3. Enable agent compatibility using the adapter instructions below.

---

## Multi-Agent Integration

Use these commands to make your skills compatible with different terminal-based AI agents. This prevents "instruction drift" by pointing every tool to the same master files.

### 1. Gemini CLI
Gemini discovers skills from directories. Link each vendor folder individually:

```bash
gemini skills link /path/to/rv-ai-skills/external/anthropic
gemini skills link /path/to/rv-ai-skills/external/vercel
gemini skills link /path/to/rv-ai-skills/external/openai
gemini skills link /path/to/rv-ai-skills/external/huggingface
```

Then run:

```bash
/memory refresh
```

### 2. Claude Code
To inject a skill into a specific project's `CLAUDE.md`:

```bash
python3 adapters/skill_loader.py external/anthropic/pdf/SKILL.md claude /path/to/your/project
```

### 3. Codex / Terminal Agents
Codex CLI reads project instructions from `AGENTS.md` in the project root.
To inject a skill into that file:

```bash
python3 adapters/skill_loader.py external/anthropic/pdf/SKILL.md codex /path/to/your/project
```

---

## Adding Skills from External Vendors

You can easily import new expertise from major AI companies by linking them from the .vendor directory.

### 1. Sync All Vendors
To pull the latest updates for every integrated vendor (Anthropic, OpenAI, etc.), run:

```bash
sh setup.sh
```

### 2. Link a Specific Skill
To add a new skill from a vendor to your active hub:
1. Find the skill in `.vendor/` (for example: `.vendor/anthropic/skills/git-flow`).
2. Create a relative symlink in the matching `external/` folder:

```bash
cd external/anthropic
ln -s ../../.vendor/anthropic/skills/git-flow git-flow
```

---

## FAQs: Symlinks and Portability

### What are Symlinks and why use them?
A symbolic link (symlink) is a "shortcut" to another file. This repo uses **relative symlinks** so that the hub remains functional even if you move it to a different folder or a new machine. The 'setup.sh' script ensures these links always find their targets in the hidden '.vendor/' folder.

### How do I update my own skills?
Edit files in `core/`. These are your personal, stable rules and can be loaded through the adapter layer into each agent environment.
