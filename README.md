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
Gemini CLI is natively compatible with this structure. Simply link the entire hub:
'gemini skills link /path/to/rv-ai-skills'

---

## Vendor Management Workflow

### 1. Synchronizing with Vendors
Update all linked skills at once:
'cd .vendor/anthropic && git pull'

### 2. Linking a New External Skill
Create a relative symlink from the vendor source into the vendor-specific external folder:
'cd external/anthropic && ln -s ../../.vendor/anthropic/skills/[skill-name] [skill-name]'

---

## FAQs

### What is a Symlink?
A symbolic link (symlink) is a special type of file that points to another file or directory. Unlike a copy, it doesn't duplicate data; it acts as a shortcut.

### Why use relative symlinks?
Relative symlinks use paths that are relative to the location of the link itself. This ensures the links remain valid even if you move the entire repository to a different folder or machine.

### How do I refresh Gemini's memory?
After adding or updating a skill, run '/memory refresh' in your session to re-index the repository.

---

## Integration Strategy

| Platform | Interface File | Adapter Template |
| :--- | :--- | :--- |
| Gemini CLI | GEMINI.md | adapters/gemini_cli.md |
| Claude Code | CLAUDE.md | adapters/claude_code.md |
| Codex / Cursor | .cursorrules | adapters/codex.md |
