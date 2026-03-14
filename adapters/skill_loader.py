#!/usr/bin/env python3
"""
RV AI Skills Hub — Skill Loader

Bridges the gap between different AI agents by delivering skills in their
expected format. Reads from _registry.yaml as the single source of truth.

Usage:
    python3 skill_loader.py --sync-all [--compact]
    python3 skill_loader.py --sync-all --include-external [--compact]
    python3 skill_loader.py <skill_path> <target> <project_path> [--compact]
    python3 skill_loader.py --validate [<skill_path>]
    python3 skill_loader.py --update-skill <skill_name>
    python3 skill_loader.py --list

Targets: claude, codex, gemini, cursor, openai
"""

import os
import re
import sys
import yaml

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
HUB_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORE_DIR = os.path.join(HUB_ROOT, 'core')
EXTERNAL_DIR = os.path.join(HUB_ROOT, 'external')
VENDOR_DIR = os.path.join(HUB_ROOT, '.vendor')
REGISTRY_PATH = os.path.join(HUB_ROOT, '_registry.yaml')

VALID_TARGETS = ['claude', 'codex', 'gemini', 'cursor', 'openai']

TARGET_FILES = {
    'claude': 'CLAUDE.md',
    'gemini': 'GEMINI.md',
    'codex':  'AGENTS.md',
}


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------
def load_registry():
    """Load and return the parsed _registry.yaml."""
    if not os.path.exists(REGISTRY_PATH):
        print(f'Error: registry not found at {REGISTRY_PATH}')
        sys.exit(1)
    with open(REGISTRY_PATH, 'r') as f:
        return yaml.safe_load(f)


# ---------------------------------------------------------------------------
# Skill resolution
# ---------------------------------------------------------------------------
def resolve_external_skill_path(vendor, skill_name, registry=None):
    """
    Resolve the best entry-point file for an external skill.

    Resolution order:
        1. Explicit entry_point from the registry (e.g., AGENTS.md for Vercel).
        2. AGENTS.md if present (compiled > source).
        3. SKILL.md (universal fallback).
    """
    reg = registry or load_registry()
    vendors_config = reg.get('vendors', {})
    vendor_config = vendors_config.get(vendor, {})
    skills_path = vendor_config.get('skills_path', 'skills')

    skill_dir = os.path.join(VENDOR_DIR, vendor, skills_path, skill_name)

    # Check for explicit entry_point in registry
    entry_point = None
    external_skills = reg.get('skills', {}).get('external', {}).get(vendor, [])
    for skill_entry in external_skills:
        if isinstance(skill_entry, dict) and skill_entry.get('name') == skill_name:
            entry_point = skill_entry.get('entry_point')
            break

    if entry_point:
        path = os.path.join(skill_dir, entry_point)
        if os.path.exists(path):
            return path

    # AGENTS.md preferred over SKILL.md (compiled > source)
    agents_path = os.path.join(skill_dir, 'AGENTS.md')
    if os.path.exists(agents_path):
        return agents_path

    skill_path = os.path.join(skill_dir, 'SKILL.md')
    if os.path.exists(skill_path):
        return skill_path

    return None


def resolve_skill_path(skill_ref):
    """
    Resolve a skill reference to an absolute file path.

    Accepts:
        - Direct file path: core/writing_good_readme.md
        - External directory: external/anthropic/pdf
        - Vendor shorthand: anthropic:pdf
    """
    # Direct file path
    if os.path.isfile(skill_ref):
        return os.path.abspath(skill_ref)

    abs_ref = os.path.join(HUB_ROOT, skill_ref) if not os.path.isabs(skill_ref) else skill_ref
    if os.path.isfile(abs_ref):
        return abs_ref

    # Vendor shorthand: vendor:skill-name
    if ':' in skill_ref and not skill_ref.startswith('core:'):
        vendor, skill_name = skill_ref.split(':', 1)
        resolved = resolve_external_skill_path(vendor, skill_name)
        if resolved:
            return resolved

    # External directory: external/vendor/skill-name
    if skill_ref.startswith('external/') or abs_ref.startswith(os.path.join(HUB_ROOT, 'external')):
        parts = skill_ref.replace('external/', '').split('/')
        if len(parts) >= 2:
            vendor, skill_name = parts[0], parts[1]
            resolved = resolve_external_skill_path(vendor, skill_name)
            if resolved:
                return resolved

    return None


def derive_skill_name(skill_path, skill_ref=''):
    """Derive a human-readable skill name from a path or reference."""
    if ':' in skill_ref and not skill_ref.startswith('core:'):
        return skill_ref  # vendor:skill-name format is already a good name

    basename = os.path.basename(skill_path)
    if basename in ('SKILL.md', 'AGENTS.md', 'README.md'):
        # Use parent directory name + grandparent for uniqueness
        parent = os.path.basename(os.path.dirname(skill_path))
        # Check if grandparent is a vendor name
        grandparent_path = os.path.dirname(os.path.dirname(skill_path))
        grandparent = os.path.basename(grandparent_path)
        # Walk up to find vendor name
        vendor = _find_vendor_in_path(skill_path)
        if vendor:
            return f'{vendor}:{parent}'
        return parent
    return basename.replace('.md', '')


def _find_vendor_in_path(path):
    """Extract vendor name from a skill path."""
    vendors = ['anthropic', 'vercel', 'openai', 'huggingface']
    parts = path.split(os.sep)
    for part in parts:
        if part in vendors:
            return part
    return None


# ---------------------------------------------------------------------------
# Idempotency
# ---------------------------------------------------------------------------
def _skill_marker(skill_name):
    return f'--- SKILL: {skill_name} ---'


def _end_marker(skill_name):
    return f'--- END SKILL: {skill_name} ---'


def _is_skill_present(target_file, skill_name):
    if not os.path.exists(target_file):
        return False
    with open(target_file, 'r') as f:
        return _skill_marker(skill_name) in f.read()


def _remove_skill_block(target_file, skill_name):
    """Remove an existing skill block from a target file. Returns True if removed."""
    if not os.path.exists(target_file):
        return False
    with open(target_file, 'r') as f:
        content = f.read()

    start_marker = _skill_marker(skill_name)
    end_marker = _end_marker(skill_name)

    start_idx = content.find(start_marker)
    if start_idx == -1:
        return False

    end_idx = content.find(end_marker, start_idx)
    if end_idx == -1:
        return False

    # Remove the block including surrounding newlines
    before = content[:start_idx].rstrip('\n')
    after = content[end_idx + len(end_marker):].lstrip('\n')
    new_content = before + ('\n\n' if before and after else '') + after

    with open(target_file, 'w') as f:
        f.write(new_content)
    return True


def _append_skill(target_file, skill_path, skill_name, compact=False):
    """Append a skill's content to a target file, wrapped in markers."""
    with open(skill_path, 'r') as s:
        content = s.read()

    if compact:
        content = _compact_content(content)

    os.makedirs(os.path.dirname(target_file) or '.', exist_ok=True)
    with open(target_file, 'a') as t:
        t.write(f'\n\n{_skill_marker(skill_name)}\n')
        t.write(content)
        t.write(f'\n{_end_marker(skill_name)}\n')


# ---------------------------------------------------------------------------
# Compact mode — strips code examples to reduce context usage
# ---------------------------------------------------------------------------
def _compact_content(content):
    """
    Strip fenced code blocks and reduce verbosity for context-constrained
    targets. Keeps headings, rules, and descriptions intact.
    """
    lines = content.split('\n')
    result = []
    in_code_block = False

    for line in lines:
        if line.strip().startswith('```'):
            if not in_code_block:
                in_code_block = True
                result.append('[code example omitted for brevity]')
            else:
                in_code_block = False
            continue
        if in_code_block:
            continue
        result.append(line)

    return '\n'.join(result)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------
REQUIRED_FRONTMATTER = ['name', 'description']
RECOMMENDED_FRONTMATTER = ['version', 'triggers', 'anti_triggers', 'tags']


def _parse_frontmatter(content):
    """Extract YAML frontmatter from a markdown file. Returns (dict, errors)."""
    if not content.startswith('---'):
        return None, ['Missing YAML frontmatter (file must start with ---)']

    end = content.find('---', 3)
    if end == -1:
        return None, ['Malformed frontmatter (no closing ---)']

    try:
        fm = yaml.safe_load(content[3:end])
        return fm, []
    except yaml.YAMLError as e:
        return None, [f'Invalid YAML in frontmatter: {e}']


def validate_skill(skill_path):
    """
    Validate a skill file for correctness. Returns (warnings, errors).
    Errors are blockers. Warnings are suggestions.
    """
    errors = []
    warnings = []

    if not os.path.exists(skill_path):
        return warnings, [f'File not found: {skill_path}']

    with open(skill_path, 'r') as f:
        content = f.read()

    if not content.strip():
        return warnings, ['File is empty']

    # Frontmatter validation
    fm, fm_errors = _parse_frontmatter(content)
    errors.extend(fm_errors)

    if fm:
        for field in REQUIRED_FRONTMATTER:
            if field not in fm:
                errors.append(f'Missing required frontmatter field: {field}')

        for field in RECOMMENDED_FRONTMATTER:
            if field not in fm:
                warnings.append(f'Missing recommended field: {field}')

        if 'triggers' in fm and not isinstance(fm['triggers'], list):
            errors.append('triggers must be a list')

        if 'anti_triggers' in fm and not isinstance(fm['anti_triggers'], list):
            errors.append('anti_triggers must be a list')

        if 'depends_on' in fm and not isinstance(fm['depends_on'], list):
            errors.append('depends_on must be a list')

    # Content validation
    body = content.split('---', 2)[-1] if content.startswith('---') else content

    if '# ' not in body:
        warnings.append('No headings found in skill body')

    if '## Acceptance Checklist' not in body and '## acceptance checklist' not in body.lower():
        warnings.append('No Acceptance Checklist section found')

    return warnings, errors


def validate_all():
    """Validate all core skills and print a report."""
    if not os.path.isdir(CORE_DIR):
        print(f'Error: core/ directory not found at {CORE_DIR}')
        return False

    skill_files = sorted([
        f for f in os.listdir(CORE_DIR)
        if f.endswith('.md') and not f.startswith('_')
    ])

    if not skill_files:
        print('No skill files found in core/.')
        return True

    all_valid = True
    for filename in skill_files:
        path = os.path.join(CORE_DIR, filename)
        warnings, errors = validate_skill(path)

        status = 'PASS' if not errors else 'FAIL'
        if errors:
            all_valid = False
        print(f'  {status}  {filename}')

        for err in errors:
            print(f'         ERROR: {err}')
        for warn in warnings:
            print(f'         WARN:  {warn}')

    print()
    if all_valid:
        print('All skills passed validation.')
    else:
        print('Some skills have errors. Fix them before syncing.')
    return all_valid


# ---------------------------------------------------------------------------
# Dependency resolution
# ---------------------------------------------------------------------------
def resolve_dependencies(skill_path):
    """
    Read depends_on from frontmatter and return resolved file paths.
    Dependencies can reference core skills by name or external skills
    with vendor:skill-name syntax.
    """
    with open(skill_path, 'r') as f:
        content = f.read()

    fm, _ = _parse_frontmatter(content)
    if not fm or 'depends_on' not in fm:
        return []

    deps = fm['depends_on']
    resolved = []

    for dep in deps:
        # Core skill reference
        core_path = os.path.join(CORE_DIR, f'{dep}.md')
        if os.path.exists(core_path):
            resolved.append(core_path)
            continue

        # Vendor shorthand
        dep_path = resolve_skill_path(dep)
        if dep_path:
            resolved.append(dep_path)
        else:
            print(f'  WARNING: Could not resolve dependency: {dep}')

    return resolved


# ---------------------------------------------------------------------------
# Sync operations
# ---------------------------------------------------------------------------
def sync_all_to_global(include_external=False, compact=False):
    """
    Sync skills to ~/.codex/AGENTS.md for global Codex access.

    By default, syncs only core/ skills. With --include-external, also syncs
    all enabled external skills from the registry.
    """
    registry = load_registry()

    # Collect core skills
    core_skills = []
    if os.path.isdir(CORE_DIR):
        core_skills = sorted([
            f for f in os.listdir(CORE_DIR)
            if f.endswith('.md') and not f.startswith('_')
        ])

    if not core_skills and not include_external:
        print('No skill files found in core/. Add .md files there first.')
        return

    # Ensure ~/.codex/ exists
    codex_dir = os.path.expanduser('~/.codex')
    os.makedirs(codex_dir, exist_ok=True)
    global_file = os.path.join(codex_dir, 'AGENTS.md')

    synced = []
    skipped = []

    # Sync core skills
    print(f'Syncing core skills to {global_file}')
    for filename in core_skills:
        skill_name = filename.replace('.md', '')
        skill_path = os.path.join(CORE_DIR, filename)

        if _is_skill_present(global_file, skill_name):
            print(f'  -- {skill_name}: already present, skipping.')
            skipped.append(skill_name)
        else:
            # Resolve and sync dependencies first
            deps = resolve_dependencies(skill_path)
            for dep_path in deps:
                dep_name = derive_skill_name(dep_path)
                if not _is_skill_present(global_file, dep_name):
                    _append_skill(global_file, dep_path, dep_name, compact=compact)
                    print(f'  ++ {dep_name}: dependency synced.')
                    synced.append(dep_name)

            _append_skill(global_file, skill_path, skill_name, compact=compact)
            print(f'  ++ {skill_name}: written.')
            synced.append(skill_name)

    # Sync external skills if requested
    if include_external:
        print()
        print('Syncing external skills...')
        external = registry.get('skills', {}).get('external', {})
        for vendor, skills in external.items():
            for skill_entry in skills:
                if isinstance(skill_entry, dict):
                    name = skill_entry['name']
                    enabled = skill_entry.get('enabled', True)
                else:
                    name = skill_entry
                    enabled = True

                if not enabled:
                    print(f'  -- {vendor}:{name}: disabled in registry, skipping.')
                    skipped.append(f'{vendor}:{name}')
                    continue

                full_name = f'{vendor}:{name}'
                if _is_skill_present(global_file, full_name):
                    print(f'  -- {full_name}: already present, skipping.')
                    skipped.append(full_name)
                    continue

                resolved = resolve_external_skill_path(vendor, name, registry)
                if resolved:
                    _append_skill(global_file, resolved, full_name, compact=compact)
                    print(f'  ++ {full_name}: written.')
                    synced.append(full_name)
                else:
                    print(f'  !! {full_name}: could not resolve. Run setup.sh first.')

    print()
    print(f'Done. {len(synced)} added, {len(skipped)} already present.')


def sync_skill(skill_ref, target_type, project_path, compact=False):
    """
    Inject a single skill into a specific agent's instruction file.

    skill_ref can be:
        - A file path: core/writing_good_readme.md
        - An external ref: external/anthropic/pdf
        - Vendor shorthand: anthropic:pdf
    """
    resolved_path = resolve_skill_path(skill_ref)
    if not resolved_path:
        print(f'Error: could not resolve skill "{skill_ref}".')
        print('Accepted formats:')
        print('  core/skill-name.md')
        print('  external/vendor/skill-name')
        print('  vendor:skill-name  (e.g., anthropic:pdf)')
        sys.exit(1)

    skill_name = derive_skill_name(resolved_path, skill_ref)

    # Resolve dependencies
    dep_paths = resolve_dependencies(resolved_path)

    if target_type == 'cursor':
        target_dir = os.path.join(project_path, '.cursor', 'rules')
        os.makedirs(target_dir, exist_ok=True)

        # Sync dependencies first
        for dep_path in dep_paths:
            dep_name = derive_skill_name(dep_path)
            dep_target = os.path.join(target_dir, f'{dep_name}.mdc')
            if not os.path.lexists(dep_target):
                os.symlink(os.path.abspath(dep_path), dep_target)
                print(f'  Linked dependency {dep_name} -> .cursor/rules/{dep_name}.mdc')

        target_file = os.path.join(target_dir, f'{skill_name.replace(":", "-")}.mdc')
        if os.path.lexists(target_file):
            os.remove(target_file)
        os.symlink(os.path.abspath(resolved_path), target_file)
        print(f'Linked {skill_name} -> .cursor/rules/{os.path.basename(target_file)}')

    elif target_type in TARGET_FILES:
        target_filename = TARGET_FILES[target_type]
        target_file = os.path.join(project_path, target_filename)

        # Sync dependencies first
        for dep_path in dep_paths:
            dep_name = derive_skill_name(dep_path)
            if not _is_skill_present(target_file, dep_name):
                _append_skill(target_file, dep_path, dep_name, compact=compact)
                print(f'  Appended dependency {dep_name} to {target_filename}.')

        if _is_skill_present(target_file, skill_name):
            print(f'{skill_name} already in {target_filename}. Skipping.')
            return

        _append_skill(target_file, resolved_path, skill_name, compact=compact)
        print(f'Appended {skill_name} to {target_filename}.')

    elif target_type == 'openai':
        print(f'--- SYSTEM PROMPT: {skill_name} ---')
        with open(resolved_path, 'r') as s:
            content = s.read()
            if compact:
                content = _compact_content(content)
            print(content)
        print('--- END SYSTEM PROMPT ---')

    else:
        print(f'Unknown target type: {target_type}')
        print(f'Valid targets: {", ".join(VALID_TARGETS)}')
        sys.exit(1)


def update_skill(skill_name):
    """
    Remove an existing skill from ~/.codex/AGENTS.md and re-inject it.
    Handles both core and external skills.
    """
    global_file = os.path.expanduser('~/.codex/AGENTS.md')

    if not os.path.exists(global_file):
        print(f'Global file not found: {global_file}')
        print('Run --sync-all first.')
        return

    if _remove_skill_block(global_file, skill_name):
        print(f'Removed old version of {skill_name}.')
    else:
        print(f'{skill_name} not found in global file. Will add it fresh.')

    # Re-resolve and append
    # Try core first
    core_path = os.path.join(CORE_DIR, f'{skill_name}.md')
    if os.path.exists(core_path):
        _append_skill(global_file, core_path, skill_name)
        print(f'Re-synced {skill_name} from core/.')
        return

    # Try vendor shorthand
    resolved = resolve_skill_path(skill_name)
    if resolved:
        _append_skill(global_file, resolved, skill_name)
        print(f'Re-synced {skill_name}.')
        return

    print(f'Warning: could not resolve {skill_name} to re-inject it.')
    print('The old version has been removed but no replacement was found.')


def list_skills():
    """Print all available skills from the registry with their status."""
    registry = load_registry()

    print('Core Skills')
    print('-' * 60)
    core_skills = registry.get('skills', {}).get('core', [])
    for skill in core_skills:
        name = skill['name']
        path = os.path.join(HUB_ROOT, skill.get('path', ''))
        exists = os.path.exists(path)
        enabled = skill.get('enabled', True)
        status = 'OK' if exists and enabled else 'MISSING' if not exists else 'DISABLED'
        version = skill.get('version', '-')
        print(f'  [{status:8s}]  {name:40s}  v{version}')

    print()
    print('External Skills')
    print('-' * 60)
    external = registry.get('skills', {}).get('external', {})
    for vendor, skills in external.items():
        print(f'  {vendor}/')
        for skill_entry in skills:
            if isinstance(skill_entry, dict):
                name = skill_entry['name']
                enabled = skill_entry.get('enabled', True)
            else:
                name = skill_entry
                enabled = True

            resolved = resolve_external_skill_path(vendor, name, registry)
            if resolved and enabled:
                status = 'OK'
            elif not enabled:
                status = 'DISABLED'
            else:
                status = 'MISSING'

            print(f'    [{status:8s}]  {name}')

    # Summary
    total_core = len(core_skills)
    total_external = sum(
        len(skills) for skills in external.values()
    )
    print()
    print(f'Total: {total_core} core + {total_external} external = {total_core + total_external} skills')


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------
def print_usage():
    print('RV AI Skills Hub — Skill Loader')
    print()
    print('Commands:')
    print('  --sync-all [--include-external] [--compact]')
    print('      Sync core skills to ~/.codex/AGENTS.md (global Codex access).')
    print('      Add --include-external to also sync all enabled vendor skills.')
    print('      Add --compact to strip code examples (saves context budget).')
    print()
    print('  <skill_ref> <target> <project_path> [--compact]')
    print('      Inject one skill into a project. Targets: claude, codex, gemini, cursor, openai')
    print('      skill_ref formats:')
    print('        core/writing_good_readme.md     (file path)')
    print('        external/anthropic/pdf           (external directory)')
    print('        anthropic:pdf                    (vendor shorthand)')
    print()
    print('  --validate [<skill_path>]')
    print('      Validate a skill file, or all core skills if no path given.')
    print()
    print('  --update-skill <skill_name>')
    print('      Remove and re-inject a skill in ~/.codex/AGENTS.md.')
    print()
    print('  --list')
    print('      List all skills from the registry with their resolution status.')


if __name__ == '__main__':
    args = sys.argv[1:]

    if not args:
        print_usage()
        sys.exit(1)

    compact = '--compact' in args
    include_external = '--include-external' in args

    # Strip flags from args for positional parsing
    positional = [a for a in args if not a.startswith('--')]
    flags = [a for a in args if a.startswith('--')]

    if '--sync-all' in flags:
        sync_all_to_global(include_external=include_external, compact=compact)

    elif '--validate' in flags:
        if positional:
            path = positional[0]
            if not os.path.isabs(path):
                path = os.path.join(HUB_ROOT, path)
            warnings, errors = validate_skill(path)
            status = 'PASS' if not errors else 'FAIL'
            print(f'{status}  {os.path.basename(path)}')
            for err in errors:
                print(f'  ERROR: {err}')
            for warn in warnings:
                print(f'  WARN:  {warn}')
            sys.exit(0 if not errors else 1)
        else:
            success = validate_all()
            sys.exit(0 if success else 1)

    elif '--update-skill' in flags:
        if not positional:
            print('Error: --update-skill requires a skill name.')
            print('Example: --update-skill writing_good_readme')
            sys.exit(1)
        update_skill(positional[0])

    elif '--list' in flags:
        list_skills()

    elif len(positional) == 3:
        sync_skill(positional[0], positional[1], positional[2], compact=compact)

    else:
        print_usage()
        sys.exit(1)
