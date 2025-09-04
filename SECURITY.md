# Security Policy

Thank you for helping keep this project and its users safe. We take security seriously and appreciate responsible reports.

---

## 📬 Reporting a Vulnerability

Please **do not open a public issue** for security problems.

- **Preferred:** Open a **Private Vulnerability Report** via GitHub Security Advisories  
  → Go to **Security** tab → **Advisories** → **Report a vulnerability**.
- If you cannot use advisories, email the maintainers (replace with your contact) and include “SECURITY” in the subject.

We’ll acknowledge your report **within 48 hours** and aim to provide a remediation plan or status update **within 5 business days**.

Include as much detail as possible:
- Affected component(s) and version/commit
- Impact and severity
- Reproduction steps (minimal PoC preferred)
- Any logs, screenshots, or crash output
- Suggested mitigation (if you have one)

Please give us **reasonable time to remediate** before any public disclosure.

---

## 🔒 Supported Versions

We generally support security fixes on:
- **`main`** (latest)
- The most recent tagged release (if releases are in use)

Older versions may not receive fixes. We recommend updating to the latest version.

---

## 🤝 Responsible Disclosure & Safe Harbor

- We will not pursue legal action for **good-faith research** that adheres to this policy.
- Avoid privacy violations, data destruction, or service disruption.
- Do not access or modify data that isn’t yours. If you encounter sensitive data (e.g., tokens), **stop, report, and delete** any local copies after confirmation.

---

## 🧪 Scope (What you may test)

This repository and its code, specifically:
- Discord slash command handlers (`src/commands/*`)
- Command registration (`register.ts`)
- Bot runtime logic (`src/index.ts`)
- Build/CI workflows under `.github/workflows/`

**Do not** test against third-party infrastructure you don’t control.

---

## 🚫 Out of Scope (Won’t be treated as a security vulnerability)

- Denial of service from excessive rate/command spam (Discord limits apply)
- Self-XSS (pasting code or tokens into your own client)
- Social engineering of maintainers or server admins
- Vulnerabilities in dependencies without a demonstrable impact on this project
- Issues requiring root/privileged local access without a clear exploit path from the app
- Missing security headers on static pages served by GitHub (outside our control)

---

## ✅ In Scope (Examples)

- **Token handling**: Leaks of `DISCORD_TOKEN`, `DISCORD_CLIENT_ID`, `DISCORD_GUILD_ID`, or other secrets
- **Auth/Z**: Ability to execute privileged actions without proper checks
- **Command injection**: Unsanitized inputs leading to RCE, SSRF, path traversal, etc.
- **Logic flaws**: Bypassing cooldowns/permissions to mass-mention or spam beyond intended scope
- **Supply chain**: Malicious dependency pinning or workflow injection via our CI configuration

---

## 🔐 Secrets & Incident Response

If you discover exposed credentials:
1. **Do not use them.**
2. Report immediately via a private channel (see Reporting).
3. We will rotate and revoke affected secrets and review audit logs.
4. Please **delete** any local copies/traces after we confirm rotation.

We rely on:
- **GitHub Actions Secrets** (for CI)
- Local **`.env`** files (never commit these)
- **Dependabot** and **npm audit** for upstream advisories

---

## 🧰 Dependencies & Updates

- We use **pnpm** with a pinned `packageManager` version.
- Automated updates via **`.github/dependabot.yml`** (npm + GitHub Actions).
- For vulnerabilities in dependencies, please reference the related CVE/GHSA and the exact path in the dependency tree (e.g., via `pnpm why`).

---

## 🧱 Hardening Checklist (Maintainers)

- Rotate bot token on suspicion or contributor turnover
- Principle of least privilege for Discord permissions/intents
- Avoid dangerous eval/exec patterns
- Validate and sanitize all user input
- Rate-limit and permissions-gate sensitive commands
- Keep `typescript`, `eslint`, `discord.js` up to date
- Use branch protection rules and required CI checks on `main`
- Ensure secrets are only in **GitHub Secrets**, not repo variables when sensitive

---

## 🙏 Acknowledgements

We’re grateful to researchers who practice responsible disclosure. If you’d like recognition, let us know how to credit you in the advisory.

---

## 📄 Disclosure Timeline (Typical)

- T0: Report received → acknowledge within **48h**
- T0 + ≤5 business days: triage + remediation plan or status
- Fix released → coordinated disclosure via GHSA advisory
