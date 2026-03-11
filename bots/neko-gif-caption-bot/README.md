# Neko GIF Caption Bot

Self-hosted Discord bot that captions GIF/APNG files with slash commands.

## What Users Get
- `/captiongif` slash command
- Top and/or bottom captions
- Font options: Impact, Arial, Comic Sans
- Outline thickness and optional background box
- Input via URL or uploaded attachment
- Output format: auto, GIF, or APNG

## Requirements
- Python 3.11+ (recommended)
- A Discord application with a bot token
- Bot invited with scopes: `bot`, `applications.commands`

## Quick Start
1. Create and activate a virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill values.
4. Run:
   ```bash
   python gifbot.py
   ```

## Environment Variables
Required:
- `DISCORD_TOKEN`
- `GUILD_ID`

Optional:
- `SYNC_GLOBAL_COMMANDS=false`
- `MAX_CONCURRENT_JOBS=2`
- `JOB_TIMEOUT_SECONDS=120`

## Docker (monorepo-safe)
From repository root:

```bash
docker build -f bots/neko-gif-caption-bot/Dockerfile \
  -t neko-gif-caption-bot:latest \
  bots/neko-gif-caption-bot

docker run --rm -it --env-file bots/neko-gif-caption-bot/.env neko-gif-caption-bot:latest
```

From bot directory:

```bash
cd bots/neko-gif-caption-bot
docker build -t neko-gif-caption-bot:latest .
docker run --rm -it --env-file .env neko-gif-caption-bot:latest
```

## License
MIT. See [LICENSE](LICENSE).
