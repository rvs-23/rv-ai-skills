# Cursor (.cursorrules) Adapter

To integrate these skills with Cursor:

1. Use the `skill_loader.py` to symlink skills into the `.cursor/rules/` directory as `.mdc` files.
2. For legacy support, copy instructions directly into the project root's `.cursorrules`.

### Commands
```bash
python3 adapters/skill_loader.py core/writing_good_readme.md cursor /path/to/project
```
