# Clip Studio Paint Presence

A tiny Windows helper that notices when Clip Studio Paint is open and gives your Discord profile a cute little artist presence.

## What It Does

- connects to the local Discord desktop app over RPC
- watches for `CLIPStudioPaint.exe`
- shows a timed Rich Presence session while you draw
- prompts once for your Discord Application ID and stores it in `.env`

## One-Time Setup

1. Create a Discord application at <https://discord.com/developers/applications>.
2. Copy the `Application ID`.
3. From the repo root, run `.\run-clip-studio-paint-presence.cmd`.
4. Paste the `Application ID` on first launch.

After that, the same launcher handles build and run for you.

## Optional Image Assets

If you upload art assets to your Discord application, set `LARGE_IMAGE_KEY`, `SMALL_IMAGE_KEY`, and the related text fields in `.env`.

## Commands

```powershell
.\run-clip-studio-paint-presence.cmd
pnpm clip-studio-paint-presence
pnpm --filter ./bots/clip-studio-paint-presence start
pnpm --filter ./bots/clip-studio-paint-presence build
pnpm --filter ./bots/clip-studio-paint-presence typecheck
pnpm --filter ./bots/clip-studio-paint-presence lint
```
