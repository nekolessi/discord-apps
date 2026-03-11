# Neko's Discord Apps Monorepo

A monorepo for all Discord bots, built with pnpm workspaces.

## Repository Layout

```text
.
|-- bots/
|   `-- neko-starter-bot/
|       |-- src/
|       |-- package.json
|       |-- README.md
|       |-- register.ts
|       `-- tsconfig.json
|-- .github/workflows/
|-- package.json
|-- pnpm-workspace.yaml
`-- README.md
```

## Requirements

- Node.js 20+
- pnpm (managed through `packageManager`)

## Quick Start

```bash
pnpm install
pnpm lint
pnpm typecheck
pnpm build
```

Run the starter bot in dev mode:

```bash
pnpm --filter ./bots/neko-starter-bot dev
```

## Add a New Bot

1. Copy `bots/neko-starter-bot` to a new folder under `bots/`.
2. Rename the package in the new bot's `package.json`.
3. Update command/runtime code and README for the new bot.
4. Run checks:

```bash
pnpm --filter ./bots/<your-bot> lint
pnpm --filter ./bots/<your-bot> typecheck
pnpm --filter ./bots/<your-bot> build
```

## Releases

Use the GitHub Actions workflow `Release Bot`:

1. Open Actions -> `Release Bot` -> `Run workflow`
2. Set `bot` (folder name under `bots/`)
3. Set `version` (example: `v1.0.0`)
4. Optional: set `publish_release=true` to publish a GitHub Release

The workflow creates a zip artifact for the selected bot and can publish it as a release asset.

## License

MIT
