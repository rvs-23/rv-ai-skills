import os
import sys

# ─────────────────────────────────────────────────────────────────────────────
# RV AI Skills Hub — Skill Loader
#
# The hub root is always two levels up from this file (adapters/skill_loader.py),
# so we can find core/ reliably regardless of where you run the script from.
# ─────────────────────────────────────────────────────────────────────────────
HUB_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORE_DIR = os.path.join(HUB_ROOT, 'core')


def _skill_marker(skill_name):
    """Return the idempotency marker string used to detect if a skill is already present."""
    return f'--- SKILL: {skill_name} ---'


def _is_skill_present(target_file, skill_name):
    """Return True if this skill has already been written to the target file."""
    if not os.path.exists(target_file):
        return False
    with open(target_file, 'r') as f:
        return _skill_marker(skill_name) in f.read()


def _append_skill(target_file, skill_path, skill_name):
    """Append a skill's content to a target file, wrapped in markers for idempotency."""
    with open(skill_path, 'r') as s, open(target_file, 'a') as t:
        t.write(f'\n\n--- SKILL: {skill_name} ---\n')
        t.write(s.read())
        t.write(f'\n--- END SKILL: {skill_name} ---\n')


def sync_all_to_global():
    """
    The main command for cross-machine setup.
    
    Reads every .md file in core/, then writes each one into the Codex global
    instructions file at ~/.codex/AGENTS.md. This file is loaded automatically
    by Codex CLI in every session on this machine, so running this once after
    cloning is all you ever need to do for Codex to discover your skills.
    """
    # Find all skill files in core/
    if not os.path.isdir(CORE_DIR):
        print(f'Error: core/ directory not found at {CORE_DIR}')
        print('Create it first and add your skill .md files inside it.')
        return

    skill_files = [
        f for f in os.listdir(CORE_DIR)
        if f.endswith('.md')
    ]

    if not skill_files:
        print('No skill files found in core/. Add .md files there first.')
        return

    # Ensure the ~/.codex/ directory exists
    codex_dir = os.path.expanduser('~/.codex')
    os.makedirs(codex_dir, exist_ok=True)
    global_agents_file = os.path.join(codex_dir, 'AGENTS.md')

    print(f'Syncing {len(skill_files)} skill(s) to {global_agents_file}')
    print()

    synced = []
    skipped = []

    for filename in sorted(skill_files):  # sorted for consistent, predictable order
        skill_name = filename.replace('.md', '')
        skill_path = os.path.join(CORE_DIR, filename)

        if _is_skill_present(global_agents_file, skill_name):
            print(f'  — {skill_name}: already present, skipping.')
            skipped.append(skill_name)
        else:
            _append_skill(global_agents_file, skill_path, skill_name)
            print(f'  ✓ {skill_name}: written.')
            synced.append(skill_name)

    print()
    print(f'Done. {len(synced)} added, {len(skipped)} already present.')
    print(f'Codex will now load these skills automatically in every session.')


def sync_skill(skill_path, target_type, project_path):
    """
    Inject a single skill into a specific agent's instruction file.
    Use this for per-project overrides or one-off injections.
    For global Codex setup, use --sync-all instead.
    """
    skill_name = os.path.basename(skill_path).replace('.md', '')

    if target_type == 'cursor':
        # Cursor reads .mdc files from .cursor/rules/ in the project directory.
        # We create a symlink so that edits to the skill file are reflected
        # in Cursor immediately, without needing to re-run this script.
        target_dir = os.path.join(project_path, '.cursor', 'rules')
        os.makedirs(target_dir, exist_ok=True)
        target_file = os.path.join(target_dir, f'{skill_name}.mdc')
        if os.path.lexists(target_file):
            os.remove(target_file)
        # Use absolute path so the symlink works regardless of working directory
        os.symlink(os.path.abspath(skill_path), target_file)
        print(f'Linked {skill_name} → .cursor/rules/{skill_name}.mdc')

    elif target_type in ['claude', 'gemini', 'codex']:
        target_map = {
            'claude': 'CLAUDE.md',
            'gemini': 'GEMINI.md',
            'codex':  'AGENTS.md',   # project-level; for global use --sync-all
        }
        target_filename = target_map[target_type]
        target_file = os.path.join(project_path, target_filename)

        if _is_skill_present(target_file, skill_name):
            print(f'{skill_name} already in {target_filename}. Skipping.')
            return

        _append_skill(target_file, skill_path, skill_name)
        print(f'Appended {skill_name} to {target_filename}.')

    elif target_type == 'openai':
        # Prints to stdout so you can copy-paste into the system prompt field.
        print(f'--- SYSTEM PROMPT: {skill_name} ---')
        with open(skill_path, 'r') as s:
            print(s.read())
        print(f'--- END SYSTEM PROMPT ---')

    else:
        print(f'Unknown target type: {target_type}')
        print('Valid targets: cursor, claude, gemini, codex, openai')
        print('For global Codex setup across all projects, use: --sync-all')


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage:')
        print('  python3 skill_loader.py --sync-all')
        print('      → Writes all core/ skills to ~/.codex/AGENTS.md (run once per machine)')
        print()
        print('  python3 skill_loader.py <skill_path> <target> <project_path>')
        print('      → Injects one skill into a specific project')
        print('      → Targets: cursor, claude, gemini, codex, openai')
        sys.exit(1)

    if sys.argv[1] == '--sync-all':
        sync_all_to_global()
    elif len(sys.argv) == 4:
        sync_skill(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        print('Error: wrong number of arguments. Run without arguments to see usage.')
        sys.exit(1)
