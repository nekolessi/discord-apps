# Neko 8-Ball Bot

A moody little fortune kitty for Discord, with classic 8-ball energy, reaction GIFs, and optional AI answers when you want extra drama.

## Features

- `/ask` for the classic magic 8-ball routine
- `/askai` for optional LLM-backed answers
- persona GIF reactions loaded from `assets/`
- guild config persistence in `guild_config.json`
- slash-command sync helpers for admins

## Requirements

- Python 3.11+
- a Discord bot token

## Quick Start

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

Keep the `assets/` folder beside the bot code. The GIFs inside it are used directly at runtime, so do not move them away from this little fortune gremlin.
