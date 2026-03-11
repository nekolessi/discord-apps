# Neko's Discord Apps

[![CI](https://github.com/nekolessi/discord-apps/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/nekolessi/discord-apps/actions/workflows/ci.yml)
[![Lint](https://github.com/nekolessi/discord-apps/actions/workflows/lint.yml/badge.svg?branch=main)](https://github.com/nekolessi/discord-apps/actions/workflows/lint.yml)
[![Release Bot](https://github.com/nekolessi/discord-apps/actions/workflows/release-bot.yml/badge.svg)](https://github.com/nekolessi/discord-apps/actions/workflows/release-bot.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Node 20+](https://img.shields.io/badge/node-20%2B-339933?logo=node.js&logoColor=white)](https://nodejs.org/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![pnpm workspace](https://img.shields.io/badge/pnpm-workspace-F69220?logo=pnpm&logoColor=white)](pnpm-workspace.yaml)

Monorepo for self-hosted Discord bots with shared release automation and CI.

## Bots

| Bot | Stack | Purpose |
| --- | --- | --- |
| `neko-starter-bot` | TypeScript + discord.js | Starter slash-command bot template |
| `neko-gif-caption-bot` | Python + discord.py | Captions GIF/APNG files from Discord |
| `neko-8ball-bot` | Python + discord.py | Persona-based 8-ball bot with GIF reactions |

## Repo Layout

```text
.
|-- bots/
|   |-- neko-starter-bot/
|   |-- neko-gif-caption-bot/
|   `-- neko-8ball-bot/
|-- scripts/
|   `-- new-bot.mjs
|-- .github/workflows/
|-- package.json
|-- pnpm-workspace.yaml
`-- README.md
```

## Quick Start

### Node workspace checks

```bash
pnpm install
pnpm check
```

`CI` runs the same Node checks and also validates Python bots by installing their requirements and compiling them.

### Run starter bot

```bash
pnpm --filter ./bots/neko-starter-bot dev
```

### Run GIF caption bot

```powershell
cd bots/neko-gif-caption-bot
python -m venv .venv
. .venv/Scripts/Activate.ps1
pip install -r requirements.txt
python gifbot.py
```

### Run 8-ball bot

```powershell
cd bots/neko-8ball-bot
python -m venv .venv
. .venv/Scripts/Activate.ps1
pip install -r requirements.txt
python neko_8ball_bot.py
```

## Scaffold a New Node Bot

```bash
pnpm new:bot neko-your-bot
```

Then run:

```bash
pnpm --filter ./bots/neko-your-bot lint
pnpm --filter ./bots/neko-your-bot typecheck
pnpm --filter ./bots/neko-your-bot build
pnpm --filter ./bots/neko-your-bot dev
```

## Release a Bot

Use GitHub Actions workflow `Release Bot`:

1. Open Actions -> `Release Bot` -> `Run workflow`.
2. Set `bot` to the folder name under `bots/` (lowercase kebab-case, example: `neko-starter-bot`).
3. Set `version` using semver format (example: `v1.0.0`).
4. Set `publish_release=true` to publish a GitHub release.

`Release Bot` supports both Node and Python bot folders.

## Security

Security policy and reporting guidance:
- [SECURITY.md](SECURITY.md)

## License

MIT - see [LICENSE](LICENSE).
