# Neko GIF Caption Bot

A self-hosted caption kitty for Discord that takes GIFs and APNGs, adds text, and sends them back looking extra dramatic.

## What Users Get

- `/captiongif`
- top and bottom caption support
- font choices: Impact, Arial, Comic Sans
- outline thickness and optional background box
- input from URL or attachment
- output as auto, GIF, or APNG

## Requirements

- Python 3.11+
- a Discord application with a bot token
- bot scopes: `bot`, `applications.commands`

## Quick Start

1. Create and activate a virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in the values.
4. Start the bot:
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

## Docker

From repository root:

```bash
docker build -f bots/neko-gif-caption-bot/Dockerfile \
  -t neko-gif-caption-bot:latest \
  bots/neko-gif-caption-bot

docker run --rm -it --env-file bots/neko-gif-caption-bot/.env neko-gif-caption-bot:latest
```

From the bot directory:

```bash
cd bots/neko-gif-caption-bot
docker build -t neko-gif-caption-bot:latest .
docker run --rm -it --env-file .env neko-gif-caption-bot:latest
```

## License

MIT. See [LICENSE](LICENSE).
