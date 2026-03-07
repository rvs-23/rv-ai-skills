---
name: core:writing-good-readme
description: Comprehensive standards for creating instruction-led, context-aware project documentation.
version: 1.2.0
triggers: ["write a README", "refactor project docs", "onboarding guide", "technical readme"]
anti_triggers: ["changelog", "license", "docstring"]
tags: [documentation, writing, onboarding, core]
---

# Writing High-Quality Project Documentation

## Trigger Conditions
- **Use When**: Initiating a new repository, refactoring existing `README.md` files for clarity, or creating specialized onboarding/technical documentation.
- **Do Not Use When**: Drafting low-level API references or internal-only developer notes.

## 1. Contextual Variants
Before writing, determine the primary audience and purpose:

### Variant A: High-Level Overview (Default)
Focus on the **"What"** and **"Why"**.
- **Outline**: A single paragraph explaining value and architecture.
- **Getting Started**: 3-step numbered path to a working state.
- **Tech Docs**: Direct links to external specs or `/docs/` subdirectories.

### Variant B: Onboarding / Junior Dev Guide
Focus on the **"How"** and **"Step-by-Step"**.
- **Detailed Scaffolding**: Explain directory structure and dependency management.
- **Contextual Notes**: Explain why certain architectural choices were made.
- **Support Section**: Where to ask questions or find "Good First Issues."

## 2. Information Hierarchy Principles
- **Visual Separation**: Use horizontal rules (`---`) to separate major conceptual blocks.
- **Judicious Highlighting**: Use **bolding** for architectural roles and key procedural terms.
- **Numbered FAQs**: Address common points of friction in a numbered list at the end.

## 3. Formatting Standards
- **Commands**: Encapsulate all terminal commands in triple backticks.
  ```bash
  sh setup.sh
  ```
- **Paths**: Use single backticks for all filenames, directories, and internal paths: `core/skill.md`.
- **Links**: Use Markdown hyperlinking: `[Technical Docs](https://docs.example.com)`. Never use raw URLs.

## 4. Visual Style and Tone
- **Strict "No Icon" Policy**: Professional, text-only aesthetic. No emojis.
- **Direct Tone**: Use imperative mood for all instructions (e.g., "Clone the repo" not "You should clone").
- **Senior-Level Precision**: Avoid fluff, marketing speak, or "AI-style" excitement.

## Acceptance Checklist
- [ ] Purpose is defined in a clear, icon-free outline.
- [ ] Instructions use the imperative mood and are numbered where sequential.
- [ ] All commands use triple backticks and all paths use single backticks.
- [ ] External references are properly hyperlinked.
- [ ] FAQ section (if present) is numbered and addresses portability/sync.
