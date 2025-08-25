# Neko's Discord Apps Repo (TypeScript + discord.js v14)

[![CI](https://github.com/nekolessi/discord-apps/.github/workflows/ci.yml/badge.svg)](https://github.com/nekolessi/discord-apps/.github/workflows/ci.yml)
[![Docker](https://img.shields.io/docker/pulls/your-docker-username/discord-bot-repo)](https://hub.docker.com/r/your-docker-username/discord-bot-repo)
[![Node.js Version](https://img.shields.io/badge/node-%3E%3D20.0.0-green)](https://nodejs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.5-blue)](https://www.typescriptlang.org/)
[![discord.js](https://img.shields.io/badge/discord.js-v14-blueviolet)](https://discord.js.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Lint](https://img.shields.io/github/actions/workflow/status/your-org/discord-bot-repo/ci.yml?label=lint)](https://github.com/your-org/discord-bot-repo/actions)

A batteries‑included template for building Discord bots with TypeScript, slash commands, Docker, and CI.


## ✨ Features
- TypeScript with strict config
- discord.js v14 with slash commands
- Clear command architecture (add commands in `src/commands`)
- Command registrar for global or guild scope
- Pino logging + pretty output in dev
- `.env` for secrets, Dockerfile, and GitHub Actions CI


## 🚀 Quick Start
1. **Install**
```bash
pnpm i # or npm i / yarn
```
2. **Configure** `.env` (see `.env.example`). You MUST set `DISCORD_TOKEN` and at least one of `GUILD_ID` or `APP_ID`.
3. **Register slash commands** (guild‑scoped for fast iteration):
```bash
pnpm register:guild
```
4. **Run the bot (dev)**
```bash
pnpm dev
```


When ready for production:
```bash
pnpm build && pnpm start
```


## 🔧 Scripts
- `dev` – run with ts-node-dev (watch mode)
- `build` – compile TypeScript
- `start` – run compiled JS
- `register:guild` – register commands to a specific guild (fast)
- `register:global` – register commands globally (propagation can take up to 1 hour)
- `typecheck` - strict TS type checking
- `lint` `lint:fix` `format` `check` – code quality tools


## 🧩 Adding a New Command
1. Create a new file in `src/commands`, e.g. `src/commands/echo.ts`.
2. Export a `SlashCommand` following the interface in `src/types.ts`.
3. Re-run `pnpm register:guild` to publish updated slash commands.


## 🔐 Environment Variables (`.env`)
See `.env.example`


## 🐳 Docker
```bash
# Build image
docker build -t discord-bot:latest .
# Run container (pass env)
docker run --rm -it --env-file .env discord-bot:latest
```


## 🧪 Testing the Bot Locally
- Invite the bot to your guild with the proper scopes: `bot applications.commands`.
- Prefer guild registration while iterating (`register:guild`).


## 📄 License
MIT
