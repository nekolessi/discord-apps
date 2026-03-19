# Neko's Discord Apps

[![CI](https://github.com/nekolessi/discord-apps/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/nekolessi/discord-apps/actions/workflows/ci.yml)
[![Lint](https://github.com/nekolessi/discord-apps/actions/workflows/lint.yml/badge.svg?branch=main)](https://github.com/nekolessi/discord-apps/actions/workflows/lint.yml)
[![Release Bot](https://github.com/nekolessi/discord-apps/actions/workflows/release-bot.yml/badge.svg)](https://github.com/nekolessi/discord-apps/actions/workflows/release-bot.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Node 20+](https://img.shields.io/badge/node-20%2B-339933?logo=node.js&logoColor=white)](https://nodejs.org/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![pnpm workspace](https://img.shields.io/badge/pnpm-workspace-F69220?logo=pnpm&logoColor=white)](pnpm-workspace.yaml)

A cozy cat tower of self-hosted Discord projects: part utility shelf, part chaos shelf, all very neko.

## What Lives In This Cat Tower

| Bot | Stack | Little job |
| --- | --- | --- |
| `neko-starter-bot` | TypeScript + discord.js | Starter slash-command bot for fresh ideas |
| `neko-gif-caption-bot` | Python + discord.py | Puts captions on GIF and APNG uploads |
| `neko-8ball-bot` | Python + discord.py | Answers questions with attitude and GIFs |
| `neko-anon-bot` | Python + discord.py | Collects anonymous comments with private mod replies |
| `neko-catgirl-bot` | Python + discord.py | Pulls random SFW and NSFW catgirl media |
| `neko-wordle-helper-bot` | Python + discord.py | Gives Wordle starters, hints, and teaching help |
| `clip-studio-paint-presence` | TypeScript + Discord RPC | Shows Discord Rich Presence while you draw |

## Layout

```text
.
|-- bots/
|   |-- neko-starter-bot/
|   |-- neko-gif-caption-bot/
|   |-- neko-8ball-bot/
|   |-- neko-anon-bot/
|   |-- neko-catgirl-bot/
|   |-- clip-studio-paint-presence/
|   `-- neko-wordle-helper-bot/
|-- scripts/
|   `-- new-bot.mjs
|-- .github/workflows/
|-- package.json
|-- pnpm-workspace.yaml
`-- README.md
```

## Quick Start

### Run shared workspace checks

```bash
pnpm install
pnpm check
```

`CI` runs the same Node checks and also installs Python requirements to make sure the Python bots still behave.

### Run the starter bot

```bash
cp bots/neko-starter-bot/.env.example bots/neko-starter-bot/.env
pnpm --filter ./bots/neko-starter-bot dev
```

### Run Clip Studio Paint Presence

```powershell
.\run-clip-studio-paint-presence.cmd
```

On first launch it asks for a Discord `Application ID`, checks that it looks valid, writes it to `bots/clip-studio-paint-presence/.env`, and then starts the app.

### Run the GIF caption bot

```powershell
cd bots/neko-gif-caption-bot
Copy-Item .env.example .env
python -m venv .venv
. .venv/Scripts/Activate.ps1
pip install -r requirements.txt
python gifbot.py
```

### Run the 8-ball bot

```powershell
cd bots/neko-8ball-bot
Copy-Item .env.example .env
python -m venv .venv
. .venv/Scripts/Activate.ps1
pip install -r requirements.txt
python neko_8ball_bot.py
```

### Run the anonymous comment bot

```powershell
cd bots/neko-anon-bot
Copy-Item .env.example .env
python -m venv .venv
. .venv/Scripts/Activate.ps1
pip install -r requirements.txt
python anonymous_feedback_bot.py
```

### Run the catgirl bot

```powershell
cd bots/neko-catgirl-bot
Copy-Item .env.example .env
python -m venv .venv
. .venv/Scripts/Activate.ps1
pip install -r requirements.txt
python catgirl_bot.py
```

### Run the Wordle helper bot

```powershell
cd bots/neko-wordle-helper-bot
Copy-Item .env.example .env
python -m venv .venv
. .venv/Scripts/Activate.ps1
pip install -r requirements.txt
python wordle_helper_bot.py
```

## Scaffold A New Node Bot

```bash
pnpm new:bot neko-your-bot
```

Then give the new kitten its usual checkup:

```bash
pnpm --filter ./bots/neko-your-bot lint
pnpm --filter ./bots/neko-your-bot typecheck
pnpm --filter ./bots/neko-your-bot build
pnpm --filter ./bots/neko-your-bot dev
```

## Release Flow

Use the GitHub Actions workflow `Release Bot`:

1. Open `Actions`.
2. Choose `Release Bot`.
3. Set `bot` to the folder name inside `bots/` such as `neko-starter-bot`.
4. Set `version` in semver format such as `v1.0.0`.
5. Set `publish_release=true` if you want a GitHub Release created too.

`Release Bot` supports both Node and Python bot folders.

## Security

Security and reporting details live in [SECURITY.md](SECURITY.md).

## License

MIT. See [LICENSE](LICENSE).
