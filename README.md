# RV AI Skills Hub

This repository is a centralized "portable brain" that stores high-fidelity instructions and procedural workflows for AI agents. It allows you to maintain a single source of truth for your coding standards, data processing rules, and vendor-provided expertise. By using a linked architecture, it ensures that your AI tools—whether Gemini, Claude, or Codex-based terminal agents—always behave with the same level of precision and consistency across different machines.

---

## Getting Started

1. **Clone the Hub**: 'git clone git@github.com:rvs-23/rv-ai-skills.git'
2. **Run Setup**: 'sh setup.sh' (This populates the hidden .vendor/ directory).
3. **Enable Compatibility**: Follow the instructions in the "Multi-Agent Integration" section below.

---

## Multi-Agent Integration

Use these commands to make your skills compatible with different terminal-based AI agents. This prevents "instruction drift" by pointing every tool to the same master files.

### 1. Gemini CLI
Gemini discovers skills from directories. Link each vendor folder individually:
- 'gemini skills link /path/to/rv-ai-skills/external/anthropic'
- 'gemini skills link /path/to/rv-ai-skills/external/vercel'
- 'gemini skills link /path/to/rv-ai-skills/external/openai'
- 'gemini skills link /path/to/rv-ai-skills/external/huggingface'
- Run '/memory refresh' to re-index.

### 2. Claude Code
To inject a skill into a specific project's 'CLAUDE.md':
'python3 adapters/skill_loader.py external/anthropic/git-flow claude /path/to/your/project'

### 3. Codex / Terminal Agents
To make a skill available to Codex-based terminal tools as a rule:
'python3 adapters/skill_loader.py external/anthropic/pdf codex /path/to/your/project'

---

## Adding Skills from External Vendors

You can easily import new expertise from major AI companies by linking them from the .vendor directory.

### 1. Sync All Vendors
To pull the latest updates for every integrated vendor (Anthropic, OpenAI, etc.):
'cd .vendor/anthropic && git pull' (Repeat for other folders in .vendor/)

### 2. Link a Specific Skill
To add a new skill from a vendor to your active hub:
1. Find the skill in '.vendor/' (e.g., '.vendor/anthropic/skills/git-flow').
2. Create a link in the 'external/' folder:
   'cd external/anthropic && ln -s ../../.vendor/anthropic/skills/git-flow git-flow'

---

## FAQs: Symlinks and Portability

### What are Symlinks and why use them?
A symbolic link (symlink) is a "shortcut" to another file. This repo uses **relative symlinks** so that the hub remains functional even if you move it to a different folder or a new machine. The 'setup.sh' script ensures these links always find their targets in the hidden '.vendor/' folder.

### How do I update my own skills?
Edit the files in the '/core' directory. These are your personal, stable rules. Once edited, they are instantly available to any tool that is linked to this hub.
