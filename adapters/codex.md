# Codex Adapter

Codex CLI and Cursor are different products and read different instruction files.

## Codex CLI

1. Place project-level instructions in `AGENTS.md`.
2. Load a skill file into `AGENTS.md`:
```bash
python3 adapters/skill_loader.py core/writing_good_readme.md codex /path/to/your/project
```
3. Keep `AGENTS.md` concise and task-focused to avoid instruction drift.
