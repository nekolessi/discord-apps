# Discord Bot — Commands & Beginner Guide

Welcome! This guide explains what commands the bot exposes and how to run, build, and deploy it locally and via GitHub Actions.

---

## Slash Commands (what your bot provides)

> All commands live under **src/commands/** and are registered via `register.ts`.

- **`/ping`**  
  Replies with `Pong!` and then reports latency.

- **`/echo text:<message>`**  
  Sends back the exact text you provide.

- **`/help`**  
  Lists the commands above with a short description.

---

## Project Structure

```
.
├── package.json
├── tsconfig.json
├── register.ts          # registers slash commands (guild/global)
├── types.ts             # shared types for commands
├── .github/workflows/
│   ├── ci.yml
│   └── register-commands.yml
└── src/
    ├── index.ts         # bot runtime
    └── commands/
        ├── ping.ts
        ├── echo.ts
        └── help.ts
```

---

## Prerequisites

- **Node.js ≥ 20**
- **pnpm** (the repo pins a version via `packageManager` in `package.json`)
- A **Discord application** with a **Bot** created in the Discord Developer Portal
- **Permissions**: make sure your bot has the *applications.commands* scope and is invited with the proper permissions to your guild if you’ll test guild commands.

---

## Environment Variables

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

## Scripts

From `package.json`:

- `pnpm dev` — run the bot in watch mode (using `src/index.ts`)
- `pnpm build` — bundle `src/index.ts` (and optionally `register.ts` if included) to `dist/`
- `pnpm start` — run the built bot (`dist/index.js`)
- `pnpm typecheck` — `tsc --noEmit`
- `pnpm check` — typecheck + lint
- `pnpm lint` / `pnpm lint:fix`
- `pnpm format` — Prettier
- `pnpm run register:guild` — register commands to a single guild (fast propagation)
- `pnpm run register:global` — register commands globally (can take ~1 hour to propagate)

---

## Run Locally

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

## Deploy / CI

### Register commands via GitHub Actions
- Workflow: `.github/workflows/register-commands.yml`
- Run it from the **Actions** tab and choose scope: `guild` or `global`.
- Make sure repo **secrets** are set:
  - `DISCORD_TOKEN`
  - `DISCORD_CLIENT_ID`
  - `DISCORD_GUILD_ID` (only for guild)

### CI (lint/typecheck/build)
- Workflow: `.github/workflows/ci.yml`
- Runs on push/PR; uses the pnpm version from `package.json`’s `packageManager`.

---

## Adding a New Slash Command

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

## Common Issues & Fixes

- **`Cannot find module '../types'`**  
  Your `types.ts` is at the repo root. In `src/index.ts` import it as:
  ```ts
  import type { SlashCommand } from "../types";
  ```
  and from `src/commands/*` as:
  ```ts
  import type { SlashCommand } from "../../types";
  ```

- **Type error: `SlashCommandOptionsOnlyBuilder` vs `SlashCommandBuilder`**  
  Widen the type in `types.ts`:
  ```ts
  import type {
    SlashCommandBuilder,
    SlashCommandOptionsOnlyBuilder,
    SlashCommandSubcommandsOnlyBuilder,
    ChatInputCommandInteraction
  } from "discord.js";

  export type SlashCommandData =
    | SlashCommandBuilder
    | SlashCommandOptionsOnlyBuilder
    | SlashCommandSubcommandsOnlyBuilder;

  export interface SlashCommand {
    data: SlashCommandData;
    execute(interaction: ChatInputCommandInteraction): Promise<void>;
  }
  ```

- **401 Unauthorized when registering**  
  - `DISCORD_TOKEN` is wrong/expired → reset token in Developer Portal.
  - `DISCORD_CLIENT_ID` doesn’t match the token’s app → copy Application ID again.
  - Secrets not available (e.g., from a fork) → run the workflow in the main repo.

- **Badge shows “repo or workflow not found”**  
  Ensure the filename matches the workflow path. Example badge:
  ```md
  ![CI](https://github.com/<USER_OR_ORG>/<REPO>/actions/workflows/ci.yml/badge.svg?branch=main)
  ![Lint](https://github.com/<USER_OR_ORG>/<REPO>/actions/workflows/lint.yml/badge.svg?branch=main)
  ![Register Commands](https://github.com/<USER_OR_ORG>/<REPO>/actions/workflows/register-commands.yml/badge.svg)
  ```

---

## Troubleshooting Checklist

- ✅ Node 20+, pnpm installed  
- ✅ `.env` present locally (or GitHub Secrets set in CI)  
- ✅ `DISCORD_CLIENT_ID` matches the app of your `DISCORD_TOKEN`  
- ✅ `DISCORD_GUILD_ID` set when using `--scope guild`  
- ✅ Commands imported and included in both the runtime (`src/index.ts`) and `register.ts`

---

## Useful Commands (one-liners)

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

Happy hacking! 🎮
