# Anonymous Comment Bot

A shy little `discord.py` helper that lets members send anonymous comments while moderators keep a private reply path.

## Requirements

- Python 3.11+
- a Discord bot token

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

- `/comment` opens the anonymous comment modal for members
- `/reply case_id:<id> message:<text>` is for moderators with `Manage Messages`
- `/help` shows command usage

## How The Bot Works

1. A member runs `/comment` and sends their message through the modal.
2. The bot posts the comment in `COMMENTS_CHANNEL_ID` with a case ID like `MEOW-0001`.
3. The bot stores `case_id -> user_id` in `CASE_STORE_PATH` so identities stay hidden in-channel.
4. A moderator runs `/reply` with the case ID and the bot sends the DM privately.
