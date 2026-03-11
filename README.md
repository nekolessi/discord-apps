# Neko's Discord Apps Monorepo

A monorepo for all Discord bots, built with pnpm workspaces.

## Bots in this repo

- `neko-starter-bot`

## Repository Layout

```text
.
|-- bots/
|   `-- neko-starter-bot/
|-- scripts/
|   `-- new-bot.mjs
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
pnpm check
```

Run starter bot in dev mode:

```bash
pnpm --filter ./bots/neko-starter-bot dev
```

## Add a New Bot (1 command)

```bash
pnpm new:bot neko-your-bot
```

That scaffolds a full bot at `bots/neko-your-bot` using the starter structure.

After scaffold:

```bash
pnpm --filter ./bots/neko-your-bot lint
pnpm --filter ./bots/neko-your-bot typecheck
pnpm --filter ./bots/neko-your-bot build
pnpm --filter ./bots/neko-your-bot dev
```

## Releases

Use GitHub Actions workflow `Release Bot`:

1. Open Actions -> `Release Bot` -> `Run workflow`
2. Set `bot` (folder name under `bots/`)
3. Set `version` (example: `v1.0.0`)
4. Optional: set `publish_release=true` to publish a GitHub release

The workflow creates a zip artifact for the selected bot and can publish it as a release asset.

## License

MIT
