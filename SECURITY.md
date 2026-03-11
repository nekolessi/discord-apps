# Security Policy

Thanks for helping keep this repository safe.

## Reporting a Vulnerability

Do not open public issues for security problems.

Use one of these options:
- GitHub Security Advisories: Security -> Advisories -> Report a vulnerability
- If advisories are unavailable, contact the maintainer privately.

Please include:
- Affected bot and file path
- Impact and severity
- Clear reproduction steps or PoC
- Any relevant logs or screenshots

Target response times:
- Initial acknowledgment: within 72 hours
- Follow-up with triage status: within 5 business days

## Supported Versions

Security fixes are provided for:
- `main` (latest)
- Latest published release tags when applicable

## Scope

In scope for this repo:
- `bots/neko-starter-bot/**`
- `bots/neko-gif-caption-bot/**`
- `.github/workflows/**`
- Root tooling and release automation

Out of scope:
- Third-party infrastructure you do not own
- Social engineering or phishing attempts
- Issues without a demonstrable impact on this repository

## Secrets and Credentials

Never post secrets in issues, PRs, or logs.

Potentially sensitive values include:
- `DISCORD_TOKEN`
- `DISCORD_CLIENT_ID`
- `DISCORD_GUILD_ID`
- `GUILD_ID`

If you suspect a secret leak:
1. Rotate the secret immediately.
2. Revoke affected credentials/tokens.
3. Report privately with timeline and scope.

## Dependency and Supply Chain

This repo uses:
- `pnpm` workspaces for Node bots
- `pip` requirements for Python bots
- Dependabot for `npm`, `pip`, and GitHub Actions updates

When reporting dependency issues, include CVE/GHSA IDs and the affected package/version.
