# OpenAI System Prompt Adapter

To use these skills with OpenAI-based agents (ChatGPT, API, Playground):

1. Use the `skill_loader.py` with the `openai` target to output a clean system prompt.
2. Copy the resulting text into the "System Instructions" or "Developer System Message" field.

### Commands
```bash
python3 adapters/skill_loader.py core/writing_good_readme.md openai .
```
