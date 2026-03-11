import { cp } from "node:fs/promises";
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const botName = process.argv[2];

if (!botName) {
  console.error("Usage: pnpm new:bot <bot-name>");
  process.exit(1);
}

if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(botName)) {
  console.error("Bot name must be lowercase kebab-case (letters, numbers, hyphens).");
  process.exit(1);
}

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(scriptDir, "..");
const botsDir = path.join(repoRoot, "bots");
const templateDir = path.join(botsDir, "neko-starter-bot");
const targetDir = path.join(botsDir, botName);

if (!existsSync(templateDir)) {
  console.error("Template bot not found: bots/neko-starter-bot");
  process.exit(1);
}

if (existsSync(targetDir)) {
  console.error(`Bot already exists: bots/${botName}`);
  process.exit(1);
}

await cp(templateDir, targetDir, {
  recursive: true,
  filter(source) {
    const base = path.basename(source);
    return base !== "dist" && base !== "node_modules";
  },
});

const packageJsonPath = path.join(targetDir, "package.json");
const packageJson = JSON.parse(readFileSync(packageJsonPath, "utf8"));
packageJson.name = `@nekolessi/${botName}`;
writeFileSync(packageJsonPath, `${JSON.stringify(packageJson, null, 2)}\n`, "utf8");

const titleCase = botName
  .split("-")
  .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
  .join(" ");

const readmePath = path.join(targetDir, "README.md");
if (existsSync(readmePath)) {
  let readme = readFileSync(readmePath, "utf8");
  readme = readme.replaceAll("neko-starter-bot", botName);
  readme = readme.replace(/^# .*$/m, `# ${titleCase}`);
  writeFileSync(readmePath, readme, "utf8");
}

const dockerfilePath = path.join(targetDir, "Dockerfile");
if (existsSync(dockerfilePath)) {
  const dockerfile = readFileSync(dockerfilePath, "utf8").replaceAll(
    "neko-starter-bot",
    botName,
  );
  writeFileSync(dockerfilePath, dockerfile, "utf8");
}

console.log(`Created bots/${botName}`);
console.log(`Next: pnpm --filter ./bots/${botName} dev`);
