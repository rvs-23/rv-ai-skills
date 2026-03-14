# RV AI Skills Hub

A centralized **"portable brain"** for AI agent instructions and procedural workflows. Encode your knowledge once as a **skill** — a structured Markdown file — and this hub delivers it automatically to whichever AI coding agents you use, on any machine.

**Supported agents**: [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview) | [Codex CLI](https://github.com/openai/codex) | [Gemini CLI](https://github.com/google-gemini/gemini-cli) | [Cursor](https://docs.cursor.com/) | [ChatGPT / OpenAI API](https://platform.openai.com/docs)

---

## Table of Contents

1. [Quick Start](#1-quick-start)
2. [Architecture](#2-architecture)
3. [Directory Structure](#3-directory-structure)
4. [How to Use with Each AI Agent](#4-how-to-use-with-each-ai-agent)
5. [Skill Loader CLI Reference](#5-skill-loader-cli-reference)
6. [Writing Your Own Skills](#6-writing-your-own-skills)
7. [External Skill Sourcing](#7-external-skill-sourcing)
8. [Cross-CLI Compatibility Matrix](#8-cross-cli-compatibility-matrix)
9. [FAQ](#9-faq)

---

## 1. Quick Start

```bash
git clone git@github.com:rvs-23/rv-ai-skills.git
cd rv-ai-skills
pip install pyyaml    # required dependency
sh setup.sh
```

`setup.sh` performs three operations in sequence:
1. Creates the directory scaffold (`core/`, `.vendor/`, `external/`).
2. Validates all core skills and syncs them to `~/.codex/AGENTS.md` for global Codex access.
3. Clones vendor repositories (Anthropic, Vercel, OpenAI, HuggingFace) into `.vendor/` and generates a `.vendor.lock` lockfile.

After setup completes, follow [Section 4](#4-how-to-use-with-each-ai-agent) for each agent you use.

---

## 2. Architecture

### Technical Overview

```
                        _registry.yaml
                    (single source of truth)
                             |
                             v
                     +-----------------+
                     |  skill_loader.py |
                     |  (adapter layer) |
                     +-----------------+
                      /   |    |   |   \
                     v    v    v   v    v
               CLAUDE.md  |  GEMINI.md |  .cursor/rules/
          (per-project)   |  (per-proj)|  (symlinks)
                          v            v
                   AGENTS.md      stdout
               (~/.codex/ global   (copy-paste
                or per-project)    for OpenAI)

    +-----------+          +------------------+
    |  core/    |          |  external/       |
    | (your     |          | (symlinks to     |
    |  skills)  |          |  .vendor/ repos) |
    +-----------+          +------------------+
                                   |
                           +---------------+
                           |   .vendor/    |
                           | anthropic/    |
                           | vercel/       |
                           | openai/       |
                           | huggingface/  |
                           +---------------+
```

### Design Principles

1. **Single source of truth**: `_registry.yaml` defines every skill, its vendor, enabled status, and entry-point resolution strategy. The loader reads the registry — not the filesystem — to decide what to sync.

2. **Push vs. pull models**: Different agents discover skills differently. The loader abstracts this away.
   - **Push** (Codex): Content must exist in a static file before the session starts.
   - **Pull** (Gemini, Claude Code, Cursor): Content is discovered at runtime from linked directories or project files.
   - **Manual** (OpenAI/ChatGPT): Content is printed to stdout for copy-paste.

3. **Vendor format resolution**: Vendors use different file structures. The loader resolves the best entry point automatically:
   - If the registry specifies an explicit `entry_point`, use it.
   - If `AGENTS.md` exists in the skill directory, prefer it (compiled > source).
   - Fall back to `SKILL.md` (universal across all vendors).

4. **Idempotency**: All sync operations use marker-based deduplication (`--- SKILL: name ---` / `--- END SKILL: name ---`). Safe to re-run at any time.

5. **Two-tier skill system**:
   - **Core skills** (`core/`): Your personal knowledge — coding standards, workflows, team conventions. Version-controlled, edit freely.
   - **External skills** (`external/`): Vendor-maintained. Exposed via symlinks to `.vendor/` clones. Never edit directly.

6. **Dependency resolution**: Skills can declare `depends_on` in frontmatter. The loader resolves and bundles dependencies automatically when syncing.

7. **Compact mode**: Large skills (e.g., Vercel's 22KB compiled rulesets) can blow context budgets. The `--compact` flag strips code examples, keeping only rules and descriptions.

8. **Reproducibility**: `setup.sh` generates `.vendor.lock` recording the git SHA of each vendor clone, so you can detect drift and reproduce exact builds.

### Data Flow

```
User writes skill in core/
        |
        v
skill_loader.py --validate      Validates frontmatter + structure
        |
        v
skill_loader.py --sync-all      Writes to ~/.codex/AGENTS.md (global)
        |
        v
skill_loader.py <ref> claude .   Appends to project CLAUDE.md
skill_loader.py <ref> gemini .   Appends to project GEMINI.md
skill_loader.py <ref> cursor .   Symlinks to .cursor/rules/
skill_loader.py <ref> openai .   Prints to stdout
```

---

## 3. Directory Structure

```
rv-ai-skills/
├── core/                        Your personal skills. Version-controlled, edit freely.
│   ├── _template.md             Template for creating new skills.
│   └── writing_good_readme.md   Example skill: documentation standards.
├── external/                    Symlinks to vendor skills. Never edit directly.
│   ├── anthropic/               11 skills (PDF, DOCX, PPTX, XLSX, etc.)
│   ├── huggingface/             5 skills (Datasets, Model Trainer, etc.)
│   ├── openai/                  14 skills (Figma, Jupyter, Notion, etc.)
│   └── vercel/                  3 skills (React, React Native, Web Design)
├── adapters/                    Integration layer.
│   ├── skill_loader.py          Multi-target skill distribution engine.
│   ├── claude_code.md           Claude Code integration guide.
│   ├── codex.md                 Codex CLI integration guide.
│   ├── gemini_cli.md            Gemini CLI integration guide.
│   ├── cursor_rules.md          Cursor integration guide.
│   └── openai_system.md         OpenAI API integration guide.
├── .vendor/                     Raw vendor git clones. Git-ignored, populated by setup.sh.
├── _registry.yaml               Single source of truth: all skills, vendors, metadata.
├── .vendor.lock                 Vendor commit SHAs for reproducibility.
├── setup.sh                     Bootstrap and update script.
└── .gitignore
```

### What Is Committed vs. Generated

| Path | Committed | Purpose |
|------|-----------|---------|
| `core/` | Yes | Your skills — the source of truth |
| `external/` symlinks | Yes | Documents which vendor skills you depend on |
| `_registry.yaml` | Yes | Skill index and vendor configuration |
| `.vendor.lock` | Yes | Reproducibility — pins vendor SHAs |
| `.vendor/` | No | Full git clones, regenerated by `setup.sh` |
| `~/.codex/AGENTS.md` | No | Machine-specific compiled output |

---

## 4. How to Use with Each AI Agent

### 4a. Claude Code

**Documentation**: [Claude Code Overview](https://docs.anthropic.com/en/docs/claude-code/overview) | [CLAUDE.md Reference](https://docs.anthropic.com/en/docs/claude-code/memory#claudemd)

**How it discovers skills**: Claude Code reads `CLAUDE.md` in the project root at session start. This is a **per-project setup**.

**Setup** — inject skills into any project:

```bash
# Inject a core skill
python3 adapters/skill_loader.py core/writing_good_readme.md claude /path/to/project

# Inject an external skill (three equivalent formats)
python3 adapters/skill_loader.py external/anthropic/pdf claude /path/to/project
python3 adapters/skill_loader.py anthropic:pdf claude /path/to/project

# Inject with compact mode (smaller context footprint)
python3 adapters/skill_loader.py anthropic:pdf claude /path/to/project --compact
```

**Verification** — open the project in Claude Code and ask:

```
What instructions are you operating under for this project? List everything in CLAUDE.md.
```

**Adding a new skill later**: Re-run the loader pointing at the new skill file. Idempotency markers prevent duplicates.

---

### 4b. Codex CLI

**Documentation**: [Codex CLI](https://github.com/openai/codex) | [AGENTS.md Reference](https://github.com/openai/codex/blob/main/docs/AGENTS.md)

**How it discovers skills**: Codex uses a **push model** — it reads `~/.codex/AGENTS.md` at session start. Nothing is pulled at runtime. Content must exist before the session begins.

**Setup — global (all projects on this machine)**:

```bash
# Core skills only (default)
python3 adapters/skill_loader.py --sync-all

# Core + all enabled external skills
python3 adapters/skill_loader.py --sync-all --include-external

# Core + externals, compact mode (recommended for large skill sets)
python3 adapters/skill_loader.py --sync-all --include-external --compact
```

**Setup — per-project override** (layers on top of global):

```bash
python3 adapters/skill_loader.py core/writing_good_readme.md codex /path/to/project
python3 adapters/skill_loader.py anthropic:pdf codex /path/to/project
```

**Updating a changed skill**:

```bash
python3 adapters/skill_loader.py --update-skill writing_good_readme
```

**Verification**:

```bash
cat ~/.codex/AGENTS.md
```

Your skills appear wrapped in `--- SKILL: name ---` markers. In a Codex session, ask:

```
Before we begin, summarise the key rules you have been given in your instructions.
```

**Important**: Codex loses precision past roughly 2,000 words. If you have many skills, use `--compact` or keep some project-level only.

---

### 4c. Gemini CLI

**Documentation**: [Gemini CLI](https://github.com/google-gemini/gemini-cli) | [Skills Reference](https://github.com/google-gemini/gemini-cli/blob/main/docs/skills.md)

**How it discovers skills**: Gemini CLI uses a **directory-based pull model**. Register a directory once with `gemini skills link` and Gemini indexes its contents automatically.

**Setup** — run once using **absolute paths** (relative paths silently fail):

```bash
gemini skills link /absolute/path/to/rv-ai-skills/core
gemini skills link /absolute/path/to/rv-ai-skills/external/anthropic
gemini skills link /absolute/path/to/rv-ai-skills/external/vercel
gemini skills link /absolute/path/to/rv-ai-skills/external/openai
gemini skills link /absolute/path/to/rv-ai-skills/external/huggingface
```

Then refresh the index:

```
/memory refresh
```

**Per-project injection** (alternative to directory linking):

```bash
python3 adapters/skill_loader.py core/writing_good_readme.md gemini /path/to/project
python3 adapters/skill_loader.py anthropic:pdf gemini /path/to/project
```

This appends to a `GEMINI.md` file in the project root.

**Adding a new skill later**: New files in linked directories are picked up automatically on the next `/memory refresh`.

**Verification**:

```
/skills list
```

---

### 4d. Cursor

**Documentation**: [Cursor Rules](https://docs.cursor.com/context/rules)

**How it discovers skills**: Cursor reads `.mdc` rule files from `.cursor/rules/` inside the project. The loader creates **symlinks** so edits to skills are reflected immediately.

**Setup**:

```bash
python3 adapters/skill_loader.py core/writing_good_readme.md cursor /path/to/project
python3 adapters/skill_loader.py anthropic:pdf cursor /path/to/project
```

**Legacy support** (Cursor below v0.45): Copy skill content directly into `.cursorrules` at the project root.

**Verification**: Open the project in Cursor, then `Cmd+Shift+P` > "Open Cursor Settings" > Rules. Your skills appear by name. In the chat (`Cmd+L`):

```
What project rules are you currently following?
```

**Troubleshooting**: If a skill is missing, inspect the symlink:

```bash
ls -la .cursor/rules/
```

A healthy entry: `skill.mdc -> /absolute/path/to/core/skill.md`. If broken, re-run the loader.

---

### 4e. ChatGPT / OpenAI API

**Documentation**: [OpenAI Platform](https://platform.openai.com/docs) | [System Instructions](https://platform.openai.com/docs/guides/text)

**How it discovers skills**: Manual copy-paste into the system prompt field.

**Setup**:

```bash
# Print to stdout — copy the output
python3 adapters/skill_loader.py core/writing_good_readme.md openai .

# Compact mode for token-limited contexts
python3 adapters/skill_loader.py anthropic:pdf openai . --compact
```

Copy the text between `--- SYSTEM PROMPT ---` markers and paste into:
- **ChatGPT**: Settings > Custom Instructions > "What would you like ChatGPT to know?"
- **API Playground**: System message field
- **Assistants API**: Instructions parameter in the assistant configuration

---

## 5. Skill Loader CLI Reference

All commands are run from the hub root directory.

### Sync all skills globally (Codex)

```bash
python3 adapters/skill_loader.py --sync-all
python3 adapters/skill_loader.py --sync-all --include-external
python3 adapters/skill_loader.py --sync-all --include-external --compact
```

### Inject a skill into a project

```bash
python3 adapters/skill_loader.py <skill_ref> <target> <project_path> [--compact]
```

**Skill reference formats**:

| Format | Example |
|--------|---------|
| File path | `core/writing_good_readme.md` |
| External directory | `external/anthropic/pdf` |
| Vendor shorthand | `anthropic:pdf` |

**Targets**: `claude`, `codex`, `gemini`, `cursor`, `openai`

### Validate skills

```bash
# Validate all core skills
python3 adapters/skill_loader.py --validate

# Validate a single file
python3 adapters/skill_loader.py --validate core/writing_good_readme.md
```

Checks: frontmatter presence, required fields (`name`, `description`), recommended fields (`version`, `triggers`, `anti_triggers`, `tags`), list types, body structure.

### Update a changed skill

```bash
python3 adapters/skill_loader.py --update-skill writing_good_readme
python3 adapters/skill_loader.py --update-skill anthropic:pdf
```

Removes the old version from `~/.codex/AGENTS.md` and re-injects the current version. No manual editing required.

### List all skills

```bash
python3 adapters/skill_loader.py --list
```

Shows all registered skills with their resolution status (`OK`, `MISSING`, `DISABLED`).

---

## 6. Writing Your Own Skills

### Creating a new skill

Copy the template and edit:

```bash
cp core/_template.md core/your_skill_name.md
```

### Skill file format

```markdown
---
name: core:your-skill-name
description: One sentence describing what this skill enables.
version: 1.0.0
triggers: ["phrase that activates this skill", "another trigger"]
anti_triggers: ["situations where this skill must not apply"]
tags: [category, subcategory]
depends_on: []
---

# Skill Title

## Trigger Conditions
- **Use When**: Specific situations this skill covers.
- **Do Not Use When**: Explicit exclusions.

## Instructions
Step-by-step guidance in imperative mood.

## Common Mistakes
What the naive approach looks like and why it fails.

## Acceptance Checklist
- [ ] First quality criterion.
- [ ] Second quality criterion.
```

### Frontmatter fields

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `name` | Yes | string | Unique identifier. Core skills use `core:` prefix. |
| `description` | Yes | string | One-line summary. Used for relevance matching. |
| `version` | Recommended | string | Semver. Increment on meaningful changes. |
| `triggers` | Recommended | list | Phrases that should activate this skill. |
| `anti_triggers` | Recommended | list | Situations where this skill must not apply. |
| `tags` | Recommended | list | Categorization labels. |
| `depends_on` | Optional | list | Other skills this one requires. Resolved automatically. |

### Style conventions

- **No emojis**: Professional, text-only aesthetic.
- **Imperative mood**: "Clone the repo" not "You should clone the repo."
- **Commands in triple backticks** with language tags (`bash`, `python`, `tsx`).
- **Paths in single backticks**: `core/skill.md`.
- **URLs as Markdown links**: `[Docs](https://example.com)`. Never raw URLs.

### After creating a skill

```bash
# Validate
python3 adapters/skill_loader.py --validate core/your_skill_name.md

# Register in _registry.yaml (add an entry under skills.core)

# Sync to Codex
python3 adapters/skill_loader.py --sync-all

# Gemini picks it up automatically on /memory refresh (core/ is already linked)

# Inject into a specific project
python3 adapters/skill_loader.py core/your_skill_name.md claude /path/to/project
```

---

## 7. External Skill Sourcing

### Updating vendor repositories

```bash
# Update all vendors and regenerate lockfile
sh setup.sh --update

# Or update a single vendor manually
cd .vendor/anthropic && git pull
```

### Adding a new vendor skill

1. Create the symlink in the appropriate `external/` subdirectory:

```bash
cd external/anthropic && ln -s ../../.vendor/anthropic/skills/new-skill new-skill
```

2. Register it in `_registry.yaml` under the vendor's skill list:

```yaml
    anthropic:
      - name: new-skill
        enabled: true
```

3. Run `sh setup.sh --link` to verify symlinks.

### Regenerating all symlinks from registry

```bash
sh setup.sh --link
```

This reads `_registry.yaml` and creates any missing symlinks, removes disabled ones.

### Vendor lockfile

`.vendor.lock` records the git SHA and date of each vendor clone:

```
anthropic: a1b2c3d4...  # 2026-03-14 10:00:00 -0400
vercel: e5f6g7h8...     # 2026-03-14 10:00:00 -0400
```

Commit this file. It enables reproducibility and drift detection — if `setup.sh --update` changes a SHA, you see it in the diff.

---

## 8. Cross-CLI Compatibility Matrix

| Capability | Claude Code | Codex CLI | Gemini CLI | Cursor | OpenAI API |
|------------|-------------|-----------|------------|--------|------------|
| **Discovery model** | Pull (CLAUDE.md) | Push (~/.codex/AGENTS.md) | Pull (directory link) | Pull (.cursor/rules/) | Manual (copy-paste) |
| **Global skills** | No native support | `~/.codex/AGENTS.md` | `gemini skills link` | No native support | N/A |
| **Per-project skills** | `CLAUDE.md` | Local `AGENTS.md` | `GEMINI.md` or linked dir | `.cursor/rules/*.mdc` | System prompt field |
| **Skill hot-reload** | Yes | No (session start only) | `/memory refresh` | Yes | N/A |
| **Context budget** | ~200K tokens | ~128K tokens | ~1M tokens | Varies by model | Varies by model |
| **Compact mode value** | Low | High | Low | Medium | High |
| **External skill support** | Yes (via loader) | Yes (via loader) | Yes (directory link) | Yes (via loader) | Yes (via loader) |
| **Dependency resolution** | Automatic | Automatic | Manual | Automatic | N/A |

### When to use `--compact`

- **Always** for Codex `--sync-all --include-external` (context limit is tight).
- **Recommended** for OpenAI API (token costs).
- **Optional** for Claude Code and Cursor (generous context).
- **Unnecessary** for Gemini CLI (1M token context).

---

## 9. FAQ

1. **Why is `~/.codex/AGENTS.md` not committed?**
   It is a machine-specific compiled output generated from `core/`. The rule: **edit skills in `core/`, run `--sync-all` to update the global file, never edit the global file directly.**

2. **Why is `.vendor/` git-ignored?**
   It contains full git clones. Nesting git repositories complicates history. The `external/` symlinks are committed — they document dependencies — while actual content is fetched fresh by `setup.sh`. `.vendor.lock` pins the exact commit SHAs.

3. **Is `--sync-all` safe to run multiple times?**
   Yes. It checks for idempotency markers and skips skills already present.

4. **How do I update a skill I already synced?**
   `python3 adapters/skill_loader.py --update-skill <name>`. This removes the old block and re-injects the current version.

5. **Why do Cursor symlinks use absolute paths but `external/` uses relative paths?**
   Cursor resolves symlinks from an unpredictable working directory — absolute paths are required. The `external/` symlinks are resolved from a known location, so relative paths keep things portable.

6. **How do I disable a vendor skill without deleting the symlink?**
   Set `enabled: false` in `_registry.yaml` for that skill. Run `sh setup.sh --link` to clean up the symlink. The skill will be excluded from `--sync-all --include-external` operations.

7. **What if `python3` or `pyyaml` is not installed?**
   `setup.sh` falls back to hardcoded vendor URLs for cloning. The skill loader and validation features require `pip install pyyaml`.

8. **How do I add skills to all my projects at once?**
   For Codex: `--sync-all` handles this globally. For Gemini: `gemini skills link` registers directories machine-wide. For Claude Code and Cursor: use a shell loop to inject into each project:
   ```bash
   for project in ~/projects/*/; do
       python3 adapters/skill_loader.py core/your-skill.md claude "$project"
   done
   ```
