# RV AI Skills Repository

A centralized, platform-agnostic source of truth for AI instructions, coding standards, and procedural workflows. This architecture ensures high-fidelity behavior across Gemini CLI, Claude Code, and Codex-based environments.

---

## Architecture Overview

- **/core**: Stable, user-defined skills. These are your fundamental instructions for active development.
- **/external**: Third-party skills organized by vendor (e.g., /external/anthropic, /external/vercel, /external/openai, /external/huggingface).
- **/.vendor**: A hidden directory containing full clones of external repositories. Ignored by git to maintain repo size.
- **/adapters**: Active "Translation Layer" for exporting core instructions into tool-specific formats.
- **_registry.yaml**: Machine-readable index for automation.

---

## Active Synchronization (Cross-Platform)

To ensure your skills run consistently across different AI tools without "Instruction Drift," use the active sync system.

### 1. Synchronizing with Cursor (Codex)
Cursor uses modular rules in '.cursor/rules/'. To sync a skill:
'python3 adapters/skill_loader.py external/anthropic/pdf cursor /path/to/your/project'
*Note: This creates a symlink so that any update to the skill hub is instantly reflected in Cursor.*

### 2. Synchronizing with Claude Code
Claude Code uses a single 'CLAUDE.md' project context. To sync a skill:
'python3 adapters/skill_loader.py external/anthropic/git-flow claude /path/to/your/project'
*Note: This appends the skill logic directly to the project brain.*

### 3. Synchronizing with Gemini CLI
Gemini CLI discoveres skills from directories containing a SKILL.md. Since this repo is a Hub, link each vendor subdirectory individually:
1. 'gemini skills link /path/to/rv-ai-skills/external/anthropic'
2. 'gemini skills link /path/to/rv-ai-skills/external/vercel'
3. 'gemini skills link /path/to/rv-ai-skills/external/openai'
4. 'gemini skills link /path/to/rv-ai-skills/external/huggingface'
5. Run '/memory refresh' in your session to re-index all linked folders.

---

## Vendor Management Workflow

### 1. Synchronizing with Vendors
Update all linked skills at once:
'cd .vendor/anthropic && git pull'

### 2. Linking a New External Skill
Create a relative symlink from the vendor source into the vendor-specific external folder:
'cd external/anthropic && ln -s ../../.vendor/anthropic/skills/[skill-name] [skill-name]'

---

## FAQ: Symlinks and Relative Paths

### What is a Symlink and why use it?
A symbolic link (symlink) is a special file that acts as a shortcut to another file or directory. This repository uses **relative symlinks** (e.g., ../../.vendor/...) instead of absolute paths. This ensures that the hub remains functional even if moved to a different directory or machine, as the internal references stay consistent with the repository's root.
