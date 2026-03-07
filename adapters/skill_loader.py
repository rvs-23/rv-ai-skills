import os
import sys
import shutil

def sync_skill(skill_path, target_type, project_path):
    skill_name = os.path.basename(skill_path).replace('.md', '')
    
    if target_type == 'cursor':
        target_dir = os.path.join(project_path, '.cursor', 'rules')
        os.makedirs(target_dir, exist_ok=True)
        target_file = os.path.join(target_dir, f'{skill_name}.mdc')
        if os.path.lexists(target_file): os.remove(target_file)
        os.symlink(os.path.abspath(skill_path), target_file)
        print(f'Linked {skill_name} to Cursor rules.')
        
    elif target_type in ['claude', 'gemini', 'codex']:
        target_map = {
            'claude': 'CLAUDE.md',
            'gemini': 'GEMINI.md',
            'codex': 'AGENTS.md'
        }
        target_file = os.path.join(project_path, target_map[target_type])
        
        # Idempotency check: check if skill name is already present
        if os.path.exists(target_file):
            with open(target_file, 'r') as f:
                if f'--- SKILL: {skill_name} ---' in f.read():
                    print(f'Skill {skill_name} already present in {target_map[target_type]}. Skipping.')
                    return

        with open(skill_path, 'r') as s, open(target_file, 'a') as t:
            t.write(f'

--- SKILL: {skill_name} ---
')
            t.write(s.read())
            t.write(f'
--- END SKILL: {skill_name} ---
')
        print(f'Appended {skill_name} to {target_map[target_type]}.')

    elif target_type == 'openai':
        print(f'--- SYSTEM PROMPT: {skill_name} ---')
        with open(skill_path, 'r') as s:
            print(s.read())
        print('--- END SYSTEM PROMPT ---')

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('Usage: python3 skill_loader.py [skill_path] [cursor|claude|gemini|codex|openai] [project_path]')
    else:
        sync_skill(sys.argv[1], sys.argv[2], sys.argv[3])
