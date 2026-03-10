# 😽 Neko's Discord Apps (TypeScript + discord.js v14)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Node.js Version](https://img.shields.io/badge/node-%3E%3D20.0.0-green)](https://nodejs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.5-blue)](https://www.typescriptlang.org/)
[![discord.js](https://img.shields.io/badge/discord.js-v14-blueviolet)](https://discord.js.org/)
[![Docker](https://img.shields.io/badge/docker-ready-2496ED?logo=docker&logoColor=white)](Dockerfile)
[![CI](https://github.com/nekolessi/discord-apps/actions/workflows/ci.yml/badge.svg)](https://github.com/nekolessi/discord-apps/actions/workflows/ci.yml)
[![Lint](https://github.com/nekolessi/discord-apps/actions/workflows/lint.yml/badge.svg?branch=main)](https://github.com/nekolessi/discord-apps/actions/workflows/lint.yml)

A batteries‑included template for building Discord bots with TypeScript, slash commands, Docker, and CI.

---

## 💾 Project Structure

```
.
├── package.json
├── tsconfig.json
├── register.ts          # registers slash commands (guild/global)
├── types.ts             # shared types for commands
├── .github/workflows/
│   ├── ci.yml
│   ├── lint.yml
│   └── register-commands.yml
└── src/
    ├── index.ts         # bot runtime
    └── commands/
        ├── ping.ts
        ├── echo.ts
        └── help.ts
```

---

## 💡 Prerequisites

- `Node.js ≥ 20`
- `pnpm` (the repo pins a version via `packageManager` in `package.json`)
- A **Discord application** with a **Bot** created in the Discord Developer Portal.
- **Permissions**: make sure your bot has the `applications.commands` scope and is invited with the proper permissions to your guild if you’ll test guild commands.

---

## ✨ Features
- TypeScript with strict config
- discord.js v14 with slash commands
- Clear command architecture (add commands in `src/commands`)
- Command registrar for global or guild scope
- Pino logging + pretty output in dev
- `.env` for secrets, Dockerfile, and GitHub Actions CI

---

## 🚀 Quick Start
1. **Install**
```bash
pnpm i # or npm i / yarn
```
2. **Configure** `.env` (see `.env.example`). You MUST set `DISCORD_TOKEN` and `DISCORD_CLIENT_ID` (plus `DISCORD_GUILD_ID` for guild scope).
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

---

## 🔧 Scripts
From `package.json`:

- `pnpm dev` — run the bot in watch mode (using `src/index.ts`)
- `pnpm build` — bundle `src/index.ts` and `register.ts` to `dist/`
- `pnpm start` — run the built bot (`dist/src/index.js`)
- `pnpm typecheck` — `tsc --noEmit`
- `pnpm check` — typecheck + lint
- `pnpm lint` / `pnpm lint:fix`
- `pnpm format` — Prettier
- `pnpm run register:guild` — register commands to a single guild (fast propagation)
- `pnpm run register:global` — register commands globally (can take ~1 hour to propagate)

1. Install deps:
   ```bash
   pnpm install
   ```

2. Start the bot (dev mode):
   ```bash
   pnpm dev
   ```

3. Register slash commands:
   - **Guild scope (recommended for testing):**
     ```bash
     pnpm run register:guild
     ```
   - **Global scope (production):**
     ```bash
     pnpm run register:global
     ```

4. Build & run the compiled bot:
   ```bash
   pnpm build
   pnpm start
   ```

---

## 🧩 Adding a New Command
1. Create a new file under `src/commands/hello.ts`:

   ```ts
   import { SlashCommandBuilder, type ChatInputCommandInteraction } from "discord.js";
   import type { SlashCommand } from "../../types";

   export const hello: SlashCommand = {
     data: new SlashCommandBuilder()
       .setName("hello")
       .setDescription("Say hi"),
     async execute(interaction: ChatInputCommandInteraction) {
       await interaction.reply("Hello there! 👋");
     },
   };
   ```

2. Import it where commands are aggregated:
   - In `src/index.ts`, add it to your `commands` array if that’s where you dispatch.
   - In `register.ts`, add it to the list that’s turned into `data.toJSON()` before upserting.

3. Re-register commands:
   ```bash
   pnpm run register:guild
   # or
   pnpm run register:global
   ```

---

## 🔐 Environment Variables (`.env`)

Create a `.env` file (for local use) at the repo root:

```env
DISCORD_TOKEN=YOUR_BOT_TOKEN
DISCORD_CLIENT_ID=YOUR_APPLICATION_ID
DISCORD_GUILD_ID=YOUR_SERVER_ID   # only required for guild-scope registration
```

> In CI, set these as **GitHub Actions Secrets** under  
> Settings → Security → Secrets and variables → Actions → “New repository secret”.

- `DISCORD_TOKEN`: the **Bot token** (Developer Portal → Bot → Reset/Copy token)
- `DISCORD_CLIENT_ID`: the **Application (Client) ID** (Developer Portal → General Information)
- `DISCORD_GUILD_ID`: your **Server ID** (enable Developer Mode in Discord → right-click server → Copy Server ID). Only needed for **guild** scope.

---

### 💽 Register commands via GitHub Actions
- Workflow: `.github/workflows/register-commands.yml`
- Run it from the **Actions** tab and choose scope: `guild` or `global`.
- Make sure repo **secrets** are set:
  - `DISCORD_TOKEN`
  - `DISCORD_CLIENT_ID`
  - `DISCORD_GUILD_ID` (only for guild)

### 💻 CI (lint/typecheck/build)
- Workflow: `.github/workflows/ci.yml`
- Runs on push/PR; uses the pnpm version from `package.json`’s `packageManager`.

---

## 🐳 Docker
```bash
# Build image
docker build -t discord-bot:latest .
# Run container (pass env)
docker run --rm -it --env-file .env discord-bot:latest
```
---

## 📝 Troubleshooting Checklist

- ✅ Node 20+, pnpm installed  
- ✅ `.env` present locally (or GitHub Secrets set in CI)  
- ✅ `DISCORD_CLIENT_ID` matches the app of your `DISCORD_TOKEN`  
- ✅ `DISCORD_GUILD_ID` set when using `--scope guild`  
- ✅ Commands imported and included in both the runtime (`src/index.ts`) and `register.ts`

---

## 🔎 Useful Commands (one-liners)

```bash
# install deps
pnpm i

# typecheck and lint
pnpm typecheck
pnpm lint

# build & run
pnpm build && pnpm start

# register commands (guild/global)
pnpm run register:guild
pnpm run register:global
```
---

## 🧪 Testing the Bot Locally
- Invite the bot to your guild with the proper scopes: `bot applications.commands`.
- Prefer guild registration while iterating (`register:guild`).

---

## 📄 License
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) © 2025 [nekolessi](https://github.com/nekolessi) made with ❤️ and a dangerous amount of caffeine.

