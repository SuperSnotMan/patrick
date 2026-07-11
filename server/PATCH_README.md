
Patrick patch:

- ai.py now loads API settings from .env instead of config.py.
- ToolManager bug fixed.
- Keep your existing main.py.
- Required .env keys:
  OPENROUTER_API_KEY (or API_KEY)
  MODEL
  OPENROUTER_BASE_URL (optional) or BASE_URL
