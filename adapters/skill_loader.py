import os
import sys
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def sync_skill(skill_path, target_type, project_path):
    skill_name = os.path.basename(skill_path).replace('.md', '')
    
    if target_type == 'cursor':
        target_dir = os.path.join(project_path, '.cursor', 'rules')
        os.makedirs(target_dir, exist_ok=True)
        target_file = os.path.join(target_dir, f'{skill_name}.mdc')
        if os.path.lexists(target_file): os.remove(target_file)
        os.symlink(os.path.abspath(skill_path), target_file)
        print(f'Linked {skill_name} to Cursor rules.')
        
    elif target_type == 'claude':
        target_file = os.path.join(project_path, 'CLAUDE.md')
        with open(skill_path, 'r') as s, open(target_file, 'a') as t:
            t.write('

' + s.read())
        print(f'Appended {skill_name} to CLAUDE.md.')

    elif target_type == 'gemini':
        target_file = os.path.join(project_path, 'GEMINI.md')
        with open(skill_path, 'r') as s, open(target_file, 'a') as t:
            t.write('

' + s.read())
        print(f'Appended {skill_name} to GEMINI.md.')

    elif target_type == 'openai':
        print(f'--- SYSTEM PROMPT: {skill_name} ---')
        with open(skill_path, 'r') as s:
            print(s.read())
        print('--- END SYSTEM PROMPT ---')

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('Usage: python3 skill_loader.py [skill_path] [cursor|claude|gemini|openai] [project_path]')
    else:
        sync_skill(sys.argv[1], sys.argv[2], sys.argv[3])
