# Neko Starter Bot

A cozy TypeScript starter bot for when you want a clean little `discord.js` base without rebuilding the scratching post from zero.

## Requirements

- Node.js 20+
- pnpm

## Environment Variables

Copy `.env.example` to `.env` and set:

```env
DISCORD_TOKEN=your-bot-token
DISCORD_CLIENT_ID=your-application-id
DISCORD_GUILD_ID=your-guild-id
NODE_ENV=development
LOG_PRETTY=true
LOG_LEVEL=info
```

## Commands

```bash
pnpm install
pnpm dev
pnpm register:guild
pnpm register:global
pnpm build
pnpm start
```

## Docker

Build from repository root:

```bash
docker build -f bots/neko-starter-bot/Dockerfile -t neko-starter-bot:latest .
```

Run with:

```bash
docker run --rm -it --env-file bots/neko-starter-bot/.env neko-starter-bot:latest
```
