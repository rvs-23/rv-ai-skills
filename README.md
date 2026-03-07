# RV AI Skills Hub

A centralized "portable brain" for AI agent instructions and procedural workflows. This repository is the single source of truth for coding standards, data processing rules, and vendor expertise — ensuring every AI tool you use behaves with the same precision and consistency, on any machine, across any project.

The core idea is simple: instead of re-explaining your preferences to each AI agent in each new project, you encode that knowledge once as a **skill**, and this hub delivers it automatically to Gemini CLI, Claude Code, Codex CLI, Cursor, and OpenAI-based tools.

---

## Table of Contents

1. [How It Works](#how-it-works)
2. [Getting Started](#getting-started)
3. [Directory Structure](#directory-structure)
4. [Multi-Agent Integration](#multi-agent-integration)
5. [Codex CLI: Global Skill Discovery](#codex-cli-global-skill-discovery)
6. [Verification: Testing Each Agent](#verification-testing-each-agent)
7. [Adding Your Own Skills](#adding-your-own-skills)
8. [External Skill Sourcing](#external-skill-sourcing)
9. [FAQ: Symlinks and Portability](#faq-symlinks-and-portability)

---

## How It Works

Each AI agent on the market has a different mechanism for loading custom instructions. Gemini CLI discovers skill *directories*. Codex CLI reads a static file called `AGENTS.md`. Cursor reads `.mdc` rule files from a `.cursor/rules/` folder. Claude Code reads `CLAUDE.md`. Rather than maintaining four separate copies of your knowledge, this hub stores skills in one place — the `core/` directory — and the `adapters/skill_loader.py` script delivers them to whichever agent you are targeting.

The distinction between **core skills** and **external skills** is important. Core skills live in `core/` and are things only you can write: your coding standards, your preferred git workflow, your data processing conventions. External skills live in `external/` and are symlinked from vendor repositories in `.vendor/` — these are maintained by Anthropic, OpenAI, Vercel, and HuggingFace, and cover general-purpose tasks like creating Word documents, generating PDFs, or building React components. You get the benefit of vendor expertise without copying files you don't own.

---

## Getting Started

After cloning the repository, a single setup command handles everything — directory scaffolding, Codex global skill injection, and vendor repository syncing — in the correct order:

```bash
git clone git@github.com:rvs-23/rv-ai-skills.git
cd rv-ai-skills
sh setup.sh
```

`setup.sh` runs three steps in sequence. First, it creates the local directory structure (`core/`, `external/`, `.vendor/`) so the hub is ready to use even before any network calls succeed. Second — and this is the critical step for Codex — it runs `python3 adapters/skill_loader.py --sync-all`, which writes every skill from `core/` into `~/.codex/AGENTS.md`. This global file is loaded by Codex CLI automatically in every session on this machine, which means Codex discovers all your skills without any per-project configuration. Third, it attempts to clone each vendor repository, reporting clearly which succeeded and which failed without aborting on the first error.

After running `setup.sh`, proceed to the [Multi-Agent Integration](#multi-agent-integration) section to connect each tool you use.

---

## Directory Structure

```
rv-ai-skills/
├── core/                        # Your personal skills — the knowledge only you have.
│   └── writing_good_readme.md   # Edit these freely; they are version-controlled.
│
├── external/                    # Symlinks to vendor skills. Never edit these directly.
│   ├── anthropic/               # Points into .vendor/anthropic/
│   ├── huggingface/             # Points into .vendor/huggingface/
│   ├── openai/                  # Points into .vendor/openai/
│   └── vercel/                  # Points into .vendor/vercel/
│
├── adapters/                    # Platform-specific integration guides and the loader.
│   ├── skill_loader.py          # The tool that delivers skills to each agent.
│   ├── claude_code.md           # How to use skills with Claude Code.
│   ├── codex.md                 # How to use skills with Codex CLI.
│   ├── cursor_rules.md          # How to use skills with Cursor IDE.
│   ├── gemini_cli.md            # How to use skills with Gemini CLI.
│   └── openai_system.md         # How to use skills with the OpenAI API.
│
├── .vendor/                     # Git clones of vendor repos. Hidden from git (see .gitignore).
├── _registry.yaml               # Index of all available skills.
├── setup.sh                     # One-command bootstrap for any machine.
└── README.md
```

---

## Multi-Agent Integration

### Gemini CLI

Gemini uses a directory-based discovery model. You register a directory once with `gemini skills link` and Gemini indexes it — making those skills available in every future session without any per-project setup.

Run the following after `setup.sh`, replacing the paths with the absolute path to your cloned hub:

```bash
gemini skills link /path/to/rv-ai-skills/core
gemini skills link /path/to/rv-ai-skills/external/anthropic
gemini skills link /path/to/rv-ai-skills/external/vercel
gemini skills link /path/to/rv-ai-skills/external/openai
gemini skills link /path/to/rv-ai-skills/external/huggingface
```

Then refresh Gemini's index so it processes the newly linked directories:

```
/memory refresh
```

If you are unsure of the absolute path, run `pwd` from inside the `rv-ai-skills` directory and prepend it manually. Relative paths are the most common reason `gemini skills link` silently fails to register a directory.

### Claude Code

Claude Code reads a `CLAUDE.md` file in the root of whichever project you are working in. Use the skill loader to inject a specific skill into that file:

```bash
python3 adapters/skill_loader.py core/writing_good_readme.md claude /path/to/your/project
```

The loader appends the skill's content wrapped in idempotency markers, so running the command twice will not duplicate the content. If you want Claude Code to have all your core skills in a project, run the command once per skill file.

For a deeper explanation of the Claude Code integration, see `adapters/claude_code.md`.

### Cursor IDE

Cursor reads `.mdc` rule files from the `.cursor/rules/` directory inside your project. The skill loader creates a symlink there — which means edits you make to a skill in `core/` are reflected in Cursor immediately, without needing to re-run the loader:

```bash
python3 adapters/skill_loader.py core/writing_good_readme.md cursor /path/to/your/project
```

For legacy Cursor support (below version 0.45), copy the skill content directly into a `.cursorrules` file at the project root instead.

For a deeper explanation, see `adapters/cursor_rules.md`.

### OpenAI API / Playground

The `openai` target prints the skill content as a formatted system prompt, ready to copy and paste into the System Instructions field in ChatGPT, the API Playground, or your OpenAI Assistant configuration:

```bash
python3 adapters/skill_loader.py core/writing_good_readme.md openai .
```

For a deeper explanation, see `adapters/openai_system.md`.

---

## Codex CLI: Global Skill Discovery

Codex CLI works differently from every other agent in this hub, and it is worth understanding why before using it.

Most agents in this hub use a *pull model* — you point them at a directory and they reach in and retrieve skills on demand. Codex uses a *push model* — it reads a static file (`AGENTS.md`) that must already contain your instructions before a session begins. Nothing is discovered automatically at runtime.

The solution is to target Codex's **global instructions file** at `~/.codex/AGENTS.md`. Codex loads this file automatically at the start of every session on your machine, regardless of which project you are in. By writing all your core skills into this one file once, every Codex session everywhere has your full knowledge base — with zero per-project setup.

`setup.sh` does this automatically, but you can also run it manually at any time:

```bash
python3 adapters/skill_loader.py --sync-all
```

This command scans everything in `core/`, checks which skills are not yet in `~/.codex/AGENTS.md`, and appends the new ones. Skills already present are skipped. This means `--sync-all` is safe to run repeatedly — it is the right command to run whenever you add a new skill to `core/` and want Codex to know about it.

**Cross-machine workflow.** When you clone this repository on a new machine, `sh setup.sh` handles the global sync automatically. The `~/.codex/AGENTS.md` file is intentionally not committed to this repository — it is a machine-specific compiled output generated from `core/`. Your source of truth is always `core/`; the global file is always derived from it.

**Per-project overrides.** If a specific project needs skills beyond your global set — for example, a project-specific API guide — you can inject a single skill into that project's local `AGENTS.md` without touching your global file:

```bash
python3 adapters/skill_loader.py core/my-api-guide.md codex /path/to/your/project
```

Codex merges the global file and any local `AGENTS.md` it finds, so project-level additions layer on top of your global skills cleanly.

For a deeper explanation of the Codex integration, see `adapters/codex.md`.

---

## Verification: Testing Each Agent

After integration, always verify that your skills are not just present in the right files but are actually influencing agent behaviour. These are two separate things — a file can be correctly placed but its content may be too long, too late in the file, or structured in a way that the agent underweights. The tests below check both.

Think of verification as having two layers. The **structural check** confirms the skill file is in the right place and the agent can see it. The **behavioural check** confirms the agent is actually following the skill's rules when doing real work.

### Verifying Gemini CLI

**Structural check:** After linking and refreshing, run this command in a Gemini CLI session:

```
/skills list
```

You should see your linked directories listed, including `core` and any `external/` vendor directories you registered. If a directory is absent, the most likely cause is that you passed a relative path to `gemini skills link` — re-run it with an absolute path.

**Behavioural check:** Ask Gemini to perform the exact task your skill governs. For `writing_good_readme.md`, the right test is:

```
Write a README for a Python CLI tool called "dataflow" that processes CSV files.
```

Then go through the skill's acceptance checklist against the output. Does it use triple backticks for commands? Is there an imperative mood throughout? No emojis? If any rule is violated, the skill content may need to be restructured — shorter, more direct instructions tend to be weighted more heavily than longer prose.

---

### Verifying Codex CLI

**Structural check:** Navigate to any project directory and inspect the global file directly:

```bash
cat ~/.codex/AGENTS.md
```

Your skill content should be present, complete, and wrapped in the `--- SKILL: name ---` markers. Also check the word count — Codex begins to lose precision on content past roughly 2,000 words. If the file has grown long from multiple skills, consider whether all of them need to be global or whether some should be project-level only.

**Behavioural check:** Open a Codex CLI session in any project directory and ask:

```
Before we begin, summarise the key rules you have been given in your instructions.
```

A correctly loaded skill will produce a summary that maps clearly to your skill's content. If the summary is vague or misses specific rules, either the file is too long or the relevant skill is positioned too late in the file. Codex weights content that appears earlier in `AGENTS.md` more heavily — put your most important skills first.

Then run the same behavioural test as Gemini to compare output across agents:

```
Write a README for a Python CLI tool called "dataflow" that processes CSV files.
```

---

### Verifying Cursor

**Structural check:** Open the project in Cursor and navigate to **Cursor Settings → Rules** (accessible via the command palette: `Cmd+Shift+P` → "Open Cursor Settings"). Your skill should appear in the rules list by name. If it is absent, inspect the symlink directly from the terminal:

```bash
ls -la .cursor/rules/
```

A healthy symlink entry looks like `writing_good_readme.mdc -> /absolute/path/to/core/writing_good_readme.md`. A broken symlink — shown in red on most terminals — means the target path no longer resolves, usually because the skill loader used a relative path. Re-run the loader from within the hub directory to regenerate the symlink with an absolute path.

Also check whether your skill file has a `globs` field in its frontmatter. A \`globs\` setting like \`*.py\` means the rule only activates when you are editing a Python file. If you test in a different file type, the rule will not fire and you will incorrectly conclude it is not loaded. Your current core skills do not define globs, so they should be active in all file types.

**Behavioural check:** Open the Cursor chat panel (`Cmd+L` on Mac, \`Ctrl+L\` on Windows and Linux) and ask:

```
What project rules are you currently following?
```

Cursor will typically list its active rule files by name and summarise their constraints. Once you have confirmed the skill is named in that response, run the same README test used for Gemini and Codex to compare output consistency across all three agents.

---

### The Cross-Agent Consistency Test

Using the same prompt — "Write a README for a Python CLI tool called dataflow that processes CSV files" — across Gemini, Codex, and Cursor is more than just convenience. It gives you a direct comparison that reveals whether your skill is genuinely portable. If all three agents produce structurally similar READMEs that follow your rules, your skill is working as intended. If one agent's output diverges significantly, it tells you something specific about how that platform weights your skill's content — and that is actionable feedback for improving either the skill itself or how it is delivered to that platform.

---

## Adding Your Own Skills

The most valuable skills in this repository are the ones you write yourself — the institutional knowledge that no vendor repo will ever have. A skill is a Markdown file in `core/` that tells an agent exactly how to handle a specific, repeatable task.

Create a new file in `core/` following this structure:

```markdown
---
name: core:your-skill-name
description: One sentence describing when to use this skill.
version: 1.0.0
triggers: ["phrase that should load this", "another trigger phrase"]
anti_triggers: ["situation where this skill does not apply"]
---

# Skill Title

## Trigger Conditions
- **Use When**: Specific situations where this skill applies.
- **Do Not Use When**: Explicit anti-triggers to prevent misuse.

## Instructions
Step-by-step expert guidance here. Be more specific than feels natural —
write for an agent that will read this once and immediately execute.

## Common Mistakes
What the naive or wrong approach looks like, and why it fails.

## Acceptance Checklist
- [ ] Criterion one
- [ ] Criterion two
```

After creating a new skill, run \`\--sync-all\` to make it available in Codex, and re-run \`gemini skills link\` for the \`core/\` directory to make it available in Gemini (Gemini will pick it up on the next \`/memory refresh\`):

```bash
python3 adapters/skill_loader.py --sync-all
```

Good candidates for your next personal core skills, in priority order, are a \`coding-standards.md\` that encodes your preferred language patterns and error-handling conventions, a \`git-workflow.md\` that defines your branching strategy and commit message format, and a \`python-style.md\` that specifies your preferred libraries and type-hint conventions. These three skills, applied consistently across every AI tool you use, will produce a noticeable and immediate improvement in output quality.

---

## External Skill Sourcing

External skills are maintained by vendors and cloned into \`.vendor/\` by \`setup.sh\`. They are made available through symlinks in \`external/\` so you get vendor updates by pulling, not by copying files.

To pull the latest changes from a vendor:

```bash
cd .vendor/anthropic && git pull
```

To add a new skill from a vendor to your active hub, create a symlink in the appropriate \`external/\` subdirectory pointing into \`.vendor/\`:

```bash
cd external/anthropic && ln -s ../../.vendor/anthropic/skills/new-skill-name new-skill-name
```

The symlinks use relative paths so the hub remains portable — moving the entire \`rv-ai-skills\` directory to a new location does not break the links.

---

## FAQ: Symlinks and Portability

**What is a symlink and why does this repo use them?**
A symbolic link is a file that points to another file, like a shortcut. This repository uses symlinks in \`external/\` to point at skills stored in \`.vendor/\`, rather than copying the files. This means updating a vendor skill is as simple as \`git pull\` in the vendor's directory — there is only ever one copy of the file, so there is no risk of the symlink version and the vendor version drifting apart.

**Why is \`.vendor/\` hidden from git?**
The \`.vendor/\` directory contains full git repository clones. Committing one git repository inside another creates a nested dependency that complicates history and clone behaviour. Instead, \`.vendor/\` is listed in \`.gitignore\` and is populated fresh by \`setup.sh\` on each machine. Your \`external/\` symlinks are committed, which documents which vendor skills you are using; the actual content is always fetched from source.

**Why is \`~/.codex/AGENTS.md\` not committed to this repository?**
It is a machine-specific, generated file — a compiled snapshot of your \`core/\` skills at a point in time. Committing it would mean committing generated output alongside the source that generates it, which creates a synchronisation burden. The rule is: edit skills in \`core/\`, run \`\--sync-all\` to update the global file, never edit the global file directly.

**What do I do when I update a skill that is already in \`~/.codex/AGENTS.md\`?**
The idempotency check in \`\--sync-all\` skips skills that are already present, so simply re-running the command will not update an existing skill. To refresh a skill that has changed, open \`~/.codex/AGENTS.md\` in any text editor, delete the block between \`--- SKILL: skill-name ---\` and \`--- END SKILL: skill-name ---\`, save the file, and then run \`\--sync-all\` again to re-inject the updated version.

**How do I update my own core skills?**
Edit the relevant \`.md\` file in \`core/\` directly. For Gemini and Cursor, the change is reflected immediately — Gemini re-reads its linked directories each session, and Cursor follows the symlink to the live file. For Codex, run \`\--sync-all\` after editing to update the global instructions file.
