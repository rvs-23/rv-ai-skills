---
name: core:writing-good-readme
description: Professional standards for creating instruction-led, icon-free README files with clear information hierarchy.
---

# Writing High-Quality Project Documentation

Follow these principles to create README files that are professional, readable, and instructionally useful for both humans and AI agents.

## 1. Information Hierarchy

- **Project Outline**: Start with a single, detailed paragraph explaining exactly what the project does, its purpose, and its value proposition.
- **Getting Started**: Provide a direct, 3-step path to running the project. Use numbered lists.
- **Technical Documentation**: Always include a section for technical deep-dives. If external documentation exists, use hyperlinks: [Technical Docs](https://example.com/docs). If local, point to the path: `/docs/technical_spec.md`.

## 2. Formatting Standards

- **Commands**: All terminal commands must be enclosed in triple backticks for clarity.
  ```bash
  git clone git@github.com:username/repo.git
  ```
- **Paths and Files**: All file paths, directory names, and specific filenames must be enclosed in single backticks: `/src/main.py` or `README.md`.
- **Links**: Use standard Markdown hyperlinking for URLs. Do not leave raw URLs in the text.

## 3. Visual Style and Tone

- **No Icons**: Avoid the use of emojis or graphical icons. Use bold headers and horizontal rules (`---`) to create visual separation.
- **Professional Tone**: Maintain a direct, senior-engineer tone. Avoid conversational filler or "AI-style" enthusiasm.
- **Direct Instructions**: Use imperative language for setup steps (e.g., "Run the script" instead of "You can now run the script").
