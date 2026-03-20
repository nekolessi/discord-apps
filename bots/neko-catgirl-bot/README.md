# Neko Catgirl Bot

A playful little Python bot that serves random catgirl media through slash commands, with a safe path for SFW servers and proper gating for NSFW use.

## Commands

- `/neko catgirl` gets a random SFW catgirl image
- `/neko nsfwcatgirl` gets a random NSFW catgirl image or animated post and only works in NSFW channels
- both commands support `media` choices: `any`, `image`, or `animated`

## Notes

- SFW media uses `nekos.best`
- if `gif` is requested for SFW, the bot uses an animated fallback from the same SFW source
- NSFW still images use `nekosapi.com`
- NSFW animated requests use `Danbooru`, which currently returns animated posts as `mp4` or `webm` rather than literal GIF files
- the bot tries to upload a Discord-playable animated file when the clip is small enough, and falls back to a direct video link when it is not

## Install

```powershell
cd bots/neko-catgirl-bot
Copy-Item .env.example .env
python -m venv .venv
. .venv/Scripts/Activate.ps1
pip install -r requirements.txt
python catgirl_bot.py
```

## Environment Variables

Required:

- `DISCORD_TOKEN`

Optional:

- `GUILD_ID` for fast per-server slash-command sync during development

## API Sources

- SFW: [nekos.best](https://nekos.best/)
- NSFW stills: [nekosapi.com](https://nekosapi.com/)
- NSFW animated: [Danbooru](https://danbooru.donmai.us/)
