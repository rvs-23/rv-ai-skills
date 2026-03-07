import os
import sys


def _append_if_missing(skill_path, target_file):
    with open(skill_path, "r", encoding="utf-8") as src:
        content = src.read().strip()
    existing = ""
    if os.path.exists(target_file):
        with open(target_file, "r", encoding="utf-8") as dst:
            existing = dst.read()
    if content in existing:
        print(f"Skill already present in {target_file}; no changes made.")
        return
    with open(target_file, "a", encoding="utf-8") as dst:
        if existing and not existing.endswith("\n"):
            dst.write("\n")
        dst.write("\n\n")
        dst.write(content)
        dst.write("\n")
    print(f"Appended skill to {target_file}.")


def sync_skill(skill_path, target_type, project_path):
    skill_path = os.path.abspath(skill_path)
    project_path = os.path.abspath(project_path)
    skill_name = os.path.basename(skill_path).replace(".md", "")

    if not os.path.exists(skill_path):
        raise FileNotFoundError(f"Skill file not found: {skill_path}")
    if not os.path.isdir(project_path):
        raise NotADirectoryError(f"Project path not found: {project_path}")

    if target_type == "cursor":
        target_dir = os.path.join(project_path, ".cursor", "rules")
        os.makedirs(target_dir, exist_ok=True)
        target_file = os.path.join(target_dir, f"{skill_name}.mdc")
        if os.path.lexists(target_file):
            os.remove(target_file)
        os.symlink(skill_path, target_file)
        print(f"Linked {skill_name} to Cursor rules: {target_file}")
    elif target_type == "claude":
        target_file = os.path.join(project_path, "CLAUDE.md")
        _append_if_missing(skill_path, target_file)
    elif target_type == "codex":
        target_file = os.path.join(project_path, "AGENTS.md")
        _append_if_missing(skill_path, target_file)
    else:
        raise ValueError("target_type must be one of: cursor, claude, codex")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python3 skill_loader.py [skill_path] [cursor|claude|codex] [project_path]")
        sys.exit(1)
    sync_skill(sys.argv[1], sys.argv[2], sys.argv[3])
