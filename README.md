# Discord Bot Repo (TypeScript + discord.js v14)


A batteries‑included template for building Discord bots with TypeScript, slash commands, Docker, and CI.


## ✨ Features
- **TypeScript** with strict config
- **discord.js v14** with slash commands
- Clear **command architecture** (add commands in `src/commands`)
- **Command registrar** script for global or guild‑scoped commands
- **Pino** logging + pretty output in dev
- **.env** for secrets, **Dockerfile**, and **GitHub Actions CI**


## 🚀 Quick Start
1. **Clone & Install**
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
- `lint` / `format` – code quality tools


## 🧩 Adding a New Command
1. Create a new file in `src/commands`, e.g. `src/commands/echo.ts`.
2. Export a `SlashCommand` following the interface in `src/types.ts`.
3. Re-run `pnpm register:guild` to publish updated slash commands.


## 🔐 Environment Variables (`.env`)
```
DISCORD_TOKEN=your-bot-token
APP_ID=your-application-id # Required for global registration
GUILD_ID=your-test-guild-id # For guild registration (dev)
NODE_ENV=development
LOG_PRETTY=true
```


## 🐳 Docker
```bash
# Build image
docker build -t discord-bot:latest .
# Run container (pass env)
docker run --rm -it --env-file .env discord-bot:latest
```


## 🧪 Testing the Bot Locally
- Invite the bot to your guild with the proper scopes: `bot applications.commands`.
- Use guild registration while iterating (`register:guild`).


## 📄 License
MIT