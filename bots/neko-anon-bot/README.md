# Anonymous Comment Bot

A Python `discord.py` bot for anonymous member comments with moderator-only private replies.

## Requirements

- Python 3.11+
- Discord bot token

## Environment Variables

Copy `.env.example` to `.env` and set:

```env
DISCORD_TOKEN=your-bot-token
COMMENTS_CHANNEL_ID=your-comments-channel-id
CASE_STORE_PATH=./data/comment-cases.json
CASE_TAG_EMOJI=🐾
GUILD_ID=your-guild-id
LOG_LEVEL=INFO
```

## Run

```powershell
cd bots/neko-anon-bot
python -m venv .venv
. .venv/Scripts/Activate.ps1
pip install -r requirements.txt
python anonymous_feedback_bot.py
```

## Slash Commands

- `/comment` opens an anonymous comment modal for members.
- `/reply case_id:<id> message:<text>` is for moderators (Manage Messages) and sends a private DM to the original submitter.
- `/help` shows command usage.

## How it works

1. A member runs `/comment` and submits the modal.
2. The bot posts a plain bot message into `COMMENTS_CHANNEL_ID` with the comment text and a sequential case ID like `MEOW-0001`.
3. The bot stores `case_id -> user_id` in `CASE_STORE_PATH` so moderators can reply without identity exposure in-channel.
4. A moderator runs `/reply` with the case ID to DM the original submitter.
