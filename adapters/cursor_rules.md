# Cursor Rules Adapter

Cursor reads either `.cursorrules` (legacy) or `.cursor/rules/*.mdc` (modular).

1. For modular rules, load a skill as a symlink:
```bash
python3 adapters/skill_loader.py core/writing_good_readme.md cursor /path/to/your/project
```
2. Verify the created file under `.cursor/rules/` points to this repository skill.
3. Prefer modular rules over a single large `.cursorrules` file.
