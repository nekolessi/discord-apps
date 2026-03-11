# Neko 8-Ball Bot

Discord 8-ball bot with persona answers, GIF reactions, and optional AI-powered responses.

## Features
- `/ask` classic 8-ball response flow
- `/askai` optional LLM-backed response
- Persona-based GIFs from `assets/`
- Guild-level config persistence (`guild_config.json`)
- Slash-command sync helpers for admins

## Requirements
- Python 3.11+
- Discord bot token

Install and run:

```bash
pip install -r requirements.txt
python neko_8ball_bot.py
```

## Environment Variables
Required:
- `DISCORD_TOKEN`

Optional:
- `GUILD_ID`
- `AI_PROVIDER` (`openai` or `anthropic`)
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `AI_MODEL`

## Assets
Keep the `assets/` folder in this bot directory. The bot uses these GIF files at runtime.
