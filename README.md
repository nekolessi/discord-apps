# Neko's Discord Apps Monorepo

A monorepo for all Discord bots, built with pnpm workspaces.

## Bots in this repo

- `neko-starter-bot` (TypeScript / discord.js)
- `neko-gif-caption-bot` (Python / discord.py)

## Repository Layout

```text
.
|-- bots/
|   |-- neko-starter-bot/
|   `-- neko-gif-caption-bot/
|-- scripts/
|   `-- new-bot.mjs
|-- .github/workflows/
|-- package.json
|-- pnpm-workspace.yaml
`-- README.md
```

## Requirements

- Node.js 20+ and pnpm (for Node bots)
- Python 3.11+ (for Python bots)

## Quick Start

```bash
pnpm install
pnpm check
```

Run starter bot in dev mode:

```bash
pnpm --filter ./bots/neko-starter-bot dev
```

Run gif caption bot:

```bash
cd bots/neko-gif-caption-bot
python -m venv .venv
. .venv/Scripts/Activate.ps1
pip install -r requirements.txt
python gifbot.py
```

## Add a New Node Bot (1 command)

```bash
pnpm new:bot neko-your-bot
```

That scaffolds a full Node bot at `bots/neko-your-bot` using the starter structure.

## Releases

Use GitHub Actions workflow `Release Bot`:

1. Open Actions -> `Release Bot` -> `Run workflow`
2. Set `bot` (folder name under `bots/`)
3. Set `version` (example: `v1.0.0`)
4. Optional: set `publish_release=true` to publish a GitHub release

`Release Bot` supports both Node and Python bot folders.

## License

MIT
