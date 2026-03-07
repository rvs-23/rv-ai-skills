---
name: core:writing-good-readme
description: Professional standards for creating icon-free, instruction-led README files with clear information hierarchy.
---

# Writing High-Quality Project Documentation

## Trigger Conditions
- **Use When**: Creating a new repository, updating existing project documentation, or refactoring `README.md` for multi-agent compatibility.
- **Do Not Use When**: Writing internal technical specs (`DOCS.md`), changelogs, or license files.

## 1. Information Hierarchy
- **Project Outline**: A single, high-fidelity paragraph explaining what the project does, its purpose, and value.
- **Getting Started**: A 3-step numbered path to execution.
- **Technical Documentation**: Link to local paths (`/docs/tech.md`) or hyperlinked URLs.

## 2. Formatting Standards
- **Commands**: Triple backticks (` ` `) for shell commands.
- **Files/Paths**: Single backticks (` `) for filenames and directories.
- **Links**: Standard Markdown hyperlinks (`[Text](URL)`).

## 3. Style and Tone
- **No Icons**: Strict prohibition of emojis or graphical icons.
- **Imperative Mood**: Use direct commands (e.g., "Run the script").

## Acceptance Checklist
- [ ] Outline accurately describes project core value.
- [ ] Setup steps are reproducible in exactly 3 steps.
- [ ] No icons/emojis are present.
- [ ] All terminal commands use triple backticks.
- [ ] All file paths use single backticks.
