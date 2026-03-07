# RV AI Skills Hub

A centralized **"portable brain"** for AI agent instructions and procedural workflows. Instead of re-explaining your preferences to each AI tool at the start of every project, you encode that knowledge once as a **skill** — a structured Markdown file — and this hub delivers it automatically to whichever agents you use, on any machine.

---

## How It Works

Every AI agent has a different mechanism for consuming custom instructions. **Gemini CLI** discovers skill directories. **Codex CLI** reads a global instructions file at startup. **Claude Code** reads a \`CLAUDE.md\` file in your project root. **Cursor** reads \`.mdc\` rule files from a \`.cursor/rules/\` folder. Rather than maintaining separate copies of your knowledge for each tool, this hub stores skills in one place and uses \`adapters/skill_loader.py\` to deliver them in the format each agent expects.

There are two kinds of skills. **Core skills** live in \`core/\` and are things only you can write — your coding standards, your git workflow, your team conventions. **External skills** live in \`external/\` and are maintained by vendors like Anthropic, OpenAI, Vercel, and HuggingFace, covering general-purpose tasks like document creation or frontend design.

---

## Getting Started

Clone the repository and run the setup script. **One command handles everything**: directory scaffolding, global Codex skill injection, and vendor repository syncing.

\`\`\`bash
git clone git@github.com:rvs-23/rv-ai-skills.git
cd rv-ai-skills
sh setup.sh
\`\`\`

After setup completes, follow the relevant sections below for each agent you use.

---

## Directory Structure

\`\`\`
rv-ai-skills/
├── core/                    # Your personal skills. Version-controlled, edit freely.
├── external/                # Symlinks to vendor skills. Never edit directly.
│   ├── anthropic/
│   ├── huggingface/
│   ├── openai/
│   └── vercel/
├── adapters/                # Integration guides and the skill loader tool.
│   ├── skill_loader.py      # Delivers skills to each agent in the right format.
│   ├── claude_code.md
│   ├── codex.md
│   ├── cursor_rules.md
│   ├── gemini_cli.md
│   └── openai_system.md
├── .vendor/                 # Raw vendor git clones. Git-ignored, populated by setup.sh.
├── _registry.yaml           # Index of all available skills.
└── setup.sh
\`\`\`

---

## Using It in Gemini CLI

### How Gemini discovers skills

Gemini CLI uses a **directory-based pull model**. You register a directory once using \`gemini skills link\`, and Gemini indexes its contents — making every skill file inside available in every future session on that machine. This is a **one-time action**, not a per-project one.

### Setup

Run the following once after cloning, using the **absolute path** to your hub. Relative paths are the most common reason \`gemini skills link\` silently fails to register a directory. If you are unsure of the absolute path, run \`pwd\` from inside \`rv-ai-skills\` and use that as your base.

\`\`\`bash
gemini skills link /absolute/path/to/rv-ai-skills/core
gemini skills link /absolute/path/to/rv-ai-skills/external/anthropic
gemini skills link /absolute/path/to/rv-ai-skills/external/vercel
gemini skills link /absolute/path/to/rv-ai-skills/external/openai
gemini skills link /absolute/path/to/rv-ai-skills/external/huggingface
\`\`\`

Then refresh Gemini's index so it processes the newly linked directories:

\`\`\`
/memory refresh
\`\`\`

### Adding a new skill later

When you add a new file to \`core/\`, Gemini picks it up **automatically** on the next \`/memory refresh\` — no re-linking required, because the entire \`core/\` directory is already registered.

### Verification

To confirm your directories are registered, open a Gemini CLI session and run:

\`\`\`
/skills list
\`\`\`

Your linked directories should appear in the output. Once you see them listed, do a **behavioural test** by asking Gemini to perform a task that one of your skills governs and check that the output follows the skill's rules. If it does not, the most likely cause is that the skill file needs to be more directive — **concise, imperative instructions** are weighted more heavily than longer prose.

---

## Using It in Codex CLI

### How Codex discovers skills

Codex CLI works fundamentally differently from Gemini and this distinction is worth understanding clearly. Codex uses a **push model**: it does not discover directories at runtime. Instead, it reads a static file that must already contain your instructions before a session begins. Nothing is pulled automatically — content must be **pushed in ahead of time**.

The right place to push is Codex's **global instructions file** at \`~/.codex/AGENTS.md\`. Codex loads this file automatically at the start of every session on your machine, regardless of which project you are in. By writing all your core skills into this one file, every Codex session everywhere has your full knowledge base with **zero per-project setup**.

### Setup: global skill discovery

\`setup.sh\` handles this automatically as part of its sequence, but you can run it manually at any time:

\`\`\`bash
python3 adapters/skill_loader.py --sync-all
\`\`\`

This command scans every \`.md\` file in \`core/\`, checks which ones are not yet present in \`~/.codex/AGENTS.md\`, and appends the new ones. Skills already present are skipped, so the command is **safe to re-run** at any time. It is the right command to run whenever you add a new skill to \`core/\`.

### Cross-machine workflow

The \`~/.codex/AGENTS.md\` file is intentionally not committed to this repository — it is a **machine-specific compiled output** generated from \`core/\`. When you clone this repository on a new machine, \`sh setup.sh\` regenerates it automatically. Your source of truth is always \`core/\`; the global file is always derived from it.

### Per-project overrides

If a specific project needs instructions beyond your global set, you can inject a skill into that project's local \`AGENTS.md\` without touching your global file:

\`\`\`bash
python3 adapters/skill_loader.py core/your-skill.md codex /path/to/your/project
\`\`\`

Codex **merges the global file and any local \`AGENTS.md\`** it finds, so project-level additions layer cleanly on top of your global skills.

### Updating a skill that is already synced

Because \`\--sync-all\` skips skills already present in the global file, updating a changed skill requires one extra step. Open \`~/.codex/AGENTS.md\` in any editor, **delete the block** between \`--- SKILL: skill-name ---\` and \`--- END SKILL: skill-name ---\`, save the file, then run \`\--sync-all\` again to re-inject the updated version.

### Verification

First, inspect the global file directly to confirm your skills are present:

\`\`\`bash
cat ~/.codex/AGENTS.md
\`\`\`

Your skill content should be there, wrapped in the \`--- SKILL: name ---\` markers. Also check the overall length — **Codex loses precision on content past roughly 2,000 words**, so if you have many skills, consider whether all of them need to be global or whether some should stay project-level only.

Then open a Codex session in any directory and ask it to reflect its own instructions:

\`\`\`
Before we begin, summarise the key rules you have been given in your instructions.
\`\`\`

A correctly loaded set of skills produces a summary that maps clearly to what you wrote. If the summary is vague or misses specific rules, the most likely cause is that the global file has grown too long, or the relevant skill appears **too far down the file**. Codex weights content that appears earlier in \`AGENTS.md\` more heavily — **order matters**.

---

## Using It in Claude Code

### How Claude Code discovers skills

Claude Code reads a \`CLAUDE.md\` file placed in the root of whichever project you are working in. This is a **per-project setup** — you inject the skills you want into that project's \`CLAUDE.md\` and Claude Code picks them up automatically when you open it.

### Setup

Navigate to your skills hub and use the loader to inject a skill into a target project:

\`\`\`bash
python3 adapters/skill_loader.py core/your-skill.md claude /path/to/your/project
\`\`\`

The loader appends the skill's content wrapped in **idempotency markers**, so running the command twice does not produce duplicate content. If you want multiple skills active in a project, run the command once per skill file.

### Adding a new skill later

When you add a new core skill and want it active in an existing project, re-run the loader pointing at the new skill file and the project path. The **idempotency check** ensures only the new skill is added.

### Verification

Open the project in Claude Code and ask:

\`\`\`
What instructions are you operating under for this project? List everything in CLAUDE.md.
\`\`\`

Claude Code will reflect the file contents. If your skills appear in the response, the integration is working. Follow up by asking it to perform a task that one of your skills governs and check the output against the skill's **acceptance checklist**.

---

## Using It in Cursor

### How Cursor discovers skills

Cursor reads \`.mdc\` rule files from a \`.cursor/rules/\` directory inside your project. The skill loader creates a **symlink** there rather than copying the file, which means edits to a skill in \`core/\` are **reflected in Cursor immediately** without needing to re-run the loader.

### Setup

\`\`\`bash
python3 adapters/skill_loader.py core/your-skill.md cursor /path/to/your/project
\`\`\`

For legacy Cursor support (below version 0.45), copy the skill content directly into a \`.cursorrules\` file at the project root instead.

### Verification

Open the project in Cursor and navigate to **Cursor Settings → Rules** (via \`Cmd+Shift+P\` → "Open Cursor Settings"). Your skill should appear in the rules list by name. If it is absent, the symlink is likely broken. Inspect it from the terminal:

\`\`\`bash
ls -la .cursor/rules/
\`\`\`

A healthy entry looks like \`your-skill.mdc -> /absolute/path/to/core/your-skill.md\`. A broken one points to a path that no longer resolves — re-run the loader from the hub directory to regenerate it with a **correct absolute path**.

Once the rule appears in the settings panel, open the Cursor chat (\`Cmd+L\`) and ask:

\`\`\`
What project rules are you currently following?
\`\`\`

Cursor will list its active rule files and summarise their content. If your skill is named in that response, the integration is complete.

---

## Using It with OpenAI API

The \`openai\` target prints a skill's content as a **formatted system prompt**, ready to paste into the System Instructions field in ChatGPT, the API Playground, or an OpenAI Assistant:

\`\`\`bash
python3 adapters/skill_loader.py core/your-skill.md openai .
\`\`\`

Copy the output between the \`--- SYSTEM PROMPT ---\` markers and paste it into your tool's **system-level instructions** field. See \`adapters/openai_system.md\` for more detail.

---

## Adding Your Own Skills

The most valuable skills in this repository are the ones you write yourself. Create a new \`.md\` file in \`core/\` following this structure:

\`\`\`markdown
---
name: core:your-skill-name
description: One sentence describing what this skill enables.
version: 1.0.0
triggers: ["phrase that should activate this", "another trigger phrase"]
anti_triggers: ["situations where this skill should not apply"]
---

# Skill Title

## Trigger Conditions
- **Use When**: The specific situations this skill covers.
- **Do Not Use When**: Explicit cases to prevent misapplication.

## Instructions
Step-by-step guidance written for an agent that will read this once and
immediately execute. Be more specific than feels natural.

## Common Mistakes
What the naive approach looks like and why it fails.

## Acceptance Checklist
- [ ] First quality criterion
- [ ] Second quality criterion
\`\`\`

After creating a new skill, propagate it with a single command:

\`\`\`bash
# Codex: adds the new skill to the global instructions file
python3 adapters/skill_loader.py --sync-all

# Gemini: run /memory refresh in a Gemini CLI session to re-index core/
\`\`\`

---

## External Skill Sourcing

External skills are maintained by vendors, cloned into \`.vendor/\` by \`setup.sh\`, and exposed through **symlinks** in \`external/\`. To pull the latest changes from a vendor:

\`\`\`bash
cd .vendor/anthropic && git pull
\`\`\`

To make a specific vendor skill available through the hub, create a symlink in the appropriate \`external/\` subdirectory:

\`\`\`bash
cd external/anthropic && ln -s ../../.vendor/anthropic/skills/skill-name skill-name
\`\`\`

---

## FAQ

1. **Why is \`~/.codex/AGENTS.md\` not committed to this repository?**
   It is a **machine-specific, compiled output** generated from \`core/\`. Committing generated output alongside the source that produces it creates a synchronisation problem. The rule is: **edit skills in \`core/\`, run \`\--sync-all\` to update the global file, and never edit the global file directly.**

2. **Why is \`.vendor/\` git-ignored?**
   It contains full git repository clones. Nesting git repositories complicates history and clone behaviour. Your \`external/\` symlinks are committed — they document which vendor skills you depend on — while the actual content is **fetched fresh by \`setup.sh\`**.

3. **Is \`\--sync-all\` safe to run multiple times?**
   **Yes.** Before writing, it checks \`~/.codex/AGENTS.md\` for the skill's idempotency marker and skips anything already present. Only genuinely new skills are appended.

4. **Why do Cursor symlinks use absolute paths but \`external/\` symlinks use relative paths?**
   Cursor resolves symlinks at load time from an unpredictable working directory, so **absolute paths** are required for reliable resolution. The \`external/\` symlinks are resolved by shell commands where the working directory is known and controlled, making **relative paths** preferable for portability if you move the hub.
