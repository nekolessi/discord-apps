# Neko Wordle Helper Bot

A clever little `discord.py` study buddy for Wordle, built to hand out starter words, solve hints, and gentle teaching instead of just blurting answers.

## Features

- `/starter` modes:
  - `balanced`
  - `vowel-heavy`
  - `consonant-heavy`
  - `hardmode-safe`
  - `daily-rotation`
- optional per-user starter save with `save_as_default=true`
- `/solve` for next-guess suggestions from clue data
- `/teach` for scoring a guess and explaining the tradeoffs
- local JSON persistence for starter preferences

## Environment Variables

Copy `.env.example` to `.env` and set:

```env
DISCORD_TOKEN=your-bot-token
GUILD_ID=your-guild-id
WORD_LIST_PATH=./data/words_5.txt
STARTER_PREFS_PATH=./data/starter_prefs.json
```

Notes:

- `GUILD_ID` is optional but recommended for instant guild sync while developing
- `WORD_LIST_PATH` defaults to `./data/words_5.txt`

## Run

```powershell
cd bots/neko-wordle-helper-bot
python -m venv .venv
. .venv/Scripts/Activate.ps1
pip install -r requirements.txt
python wordle_helper_bot.py
```

## Clue Format

- `pattern`: exactly 5 characters of letters or `_`, for example `_r__e`
- `yellow`: comma-separated `letter+position` pairs using 1-based positions, for example `a2,r5`
- `absent`: letters known not to appear, for example `tns`
