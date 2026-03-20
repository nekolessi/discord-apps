import { execFile } from "node:child_process";
import { access, readFile, writeFile } from "node:fs/promises";
import { stdin as input, stdout as output } from "node:process";
import process from "node:process";
import path from "node:path";
import readline from "node:readline/promises";
import { promisify } from "node:util";
import { fileURLToPath } from "node:url";

import { Client } from "@xhayper/discord-rpc";
import { config as loadEnv } from "dotenv";
import { z } from "zod";

const execFileAsync = promisify(execFile);
const projectDir = fileURLToPath(new URL("../", import.meta.url));
const envPath = path.join(projectDir, ".env");
const envExamplePath = path.join(projectDir, ".env.example");
const discordApplicationIdSchema = z
  .string()
  .trim()
  .regex(/^\d{17,20}$/, "Discord Application ID must be a 17 to 20 digit number.");

await ensureEnvFile();
loadEnv({ path: envPath, quiet: true });
await ensureApplicationId();

const optionalTextSchema = z.preprocess(normalizeEnvValue, z.string().min(1).optional());
const optionalUrlSchema = z.preprocess(normalizeEnvValue, z.string().url().optional());

const env = z
  .object({
    DISCORD_APPLICATION_ID: discordApplicationIdSchema,
    CLIP_STUDIO_PROCESS_NAME: z.string().min(1).default("CLIPStudioPaint.exe"),
    POLL_INTERVAL_MS: z.coerce.number().int().min(1000).max(60000).default(5000),
    ACTIVITY_DETAILS: z.string().min(1).default("Drawing in Clip Studio Paint"),
    ACTIVITY_STATE: z.string().min(1).default("Working on a canvas"),
    SHOW_ELAPSED_TIME: z.enum(["true", "false"]).default("true"),
    LARGE_IMAGE_KEY: optionalTextSchema,
    LARGE_IMAGE_TEXT: optionalTextSchema,
    SMALL_IMAGE_KEY: optionalTextSchema,
    SMALL_IMAGE_TEXT: optionalTextSchema,
    BUTTON_LABEL: optionalTextSchema,
    BUTTON_URL: optionalUrlSchema,
  })
  .parse(process.env);

const client = new Client({ clientId: env.DISCORD_APPLICATION_ID });

let shouldExit = false;
let clipStudioStartedAt: number | null = null;
let activityActive = false;
let isDiscordReady = false;
let isDiscordConnecting = false;
let reconnectTimer: NodeJS.Timeout | null = null;

client.on("ready", () => {
  isDiscordReady = true;
  isDiscordConnecting = false;
  log("Connected to Discord RPC.");
  void syncPresence();
});

log(`Watching ${env.CLIP_STUDIO_PROCESS_NAME} for Discord Rich Presence updates.`);
void connectDiscord();
const pollTimer = setInterval(() => {
  void syncPresence();
}, env.POLL_INTERVAL_MS);

process.on("SIGINT", () => {
  void shutdown(pollTimer);
});

process.on("SIGTERM", () => {
  void shutdown(pollTimer);
});

async function syncPresence(): Promise<void> {
  if (shouldExit) {
    return;
  }

  const clipStudioRunning = await isProcessRunning(env.CLIP_STUDIO_PROCESS_NAME);

  if (!clipStudioRunning) {
    clipStudioStartedAt = null;
    if (activityActive) {
      await clearActivity();
      activityActive = false;
      log("Clip Studio Paint closed. Cleared Discord activity.");
    }
    return;
  }

  if (clipStudioStartedAt === null) {
    clipStudioStartedAt = Date.now();
    log("Clip Studio Paint detected. Waiting for Discord to accept activity.");
  }

  if (!isDiscordReady) {
    await connectDiscord();
    return;
  }

  try {
    await client.user?.setActivity({
      details: env.ACTIVITY_DETAILS,
      state: env.ACTIVITY_STATE,
      startTimestamp: env.SHOW_ELAPSED_TIME === "true" ? clipStudioStartedAt : undefined,
      largeImageKey: normalizeOptional(env.LARGE_IMAGE_KEY),
      largeImageText: normalizeOptional(env.LARGE_IMAGE_TEXT),
      smallImageKey: normalizeOptional(env.SMALL_IMAGE_KEY),
      smallImageText: normalizeOptional(env.SMALL_IMAGE_TEXT),
      buttons:
        env.BUTTON_LABEL && env.BUTTON_URL
          ? [{ label: env.BUTTON_LABEL, url: env.BUTTON_URL }]
          : undefined,
      instance: true,
    });
    if (!activityActive) {
      activityActive = true;
      log("Discord Rich Presence is live.");
    }
  } catch (error) {
    activityActive = false;
    isDiscordReady = false;
    log(`Failed to update activity: ${formatError(error)}`);
    await connectDiscord();
  }
}

async function connectDiscord(): Promise<void> {
  if (shouldExit || isDiscordReady || isDiscordConnecting) {
    return;
  }

  isDiscordConnecting = true;
  try {
    await client.login();
  } catch (error) {
    isDiscordConnecting = false;
    log(`Discord RPC connection failed: ${formatError(error)}`);
    scheduleReconnect();
  }
}

function scheduleReconnect(): void {
  if (reconnectTimer) {
    return;
  }

  reconnectTimer = setTimeout(() => {
    reconnectTimer = null;
    void connectDiscord();
  }, 5000);
}

async function clearActivity(): Promise<void> {
  try {
    await client.user?.clearActivity();
  } catch (error) {
    log(`Failed to clear activity cleanly: ${formatError(error)}`);
  }
}

async function shutdown(pollTimerHandle: NodeJS.Timeout): Promise<void> {
  if (shouldExit) {
    return;
  }

  shouldExit = true;
  clearInterval(pollTimerHandle);
  if (reconnectTimer) {
    clearTimeout(reconnectTimer);
  }

  await clearActivity();
  log("Shutting down Clip Studio Paint presence.");
  process.exit(0);
}

async function isProcessRunning(processName: string): Promise<boolean> {
  try {
    const { stdout } = await execFileAsync(
      "tasklist",
      ["/fo", "csv", "/nh", "/fi", `imagename eq ${processName}`],
      { windowsHide: true },
    );

    return stdout.toLowerCase().includes(processName.toLowerCase());
  } catch (error) {
    log(`Failed to check process list: ${formatError(error)}`);
    return false;
  }
}

async function ensureEnvFile(): Promise<void> {
  try {
    await access(envPath);
  } catch {
    const exampleContent = await readFile(envExamplePath, "utf8");
    await writeFile(envPath, exampleContent, "utf8");
  }
}

async function ensureApplicationId(): Promise<void> {
  const existingApplicationId = process.env.DISCORD_APPLICATION_ID?.trim();
  if (existingApplicationId) {
    const validationResult = discordApplicationIdSchema.safeParse(existingApplicationId);
    if (!validationResult.success) {
      throw new Error(validationResult.error.issues[0]?.message ?? "Discord Application ID is invalid.");
    }
    return;
  }

  const prompt = [
    "",
    "Create a Discord app at https://discord.com/developers/applications",
    "Paste its Application ID below. This is saved to bots/clip-studio-paint-presence/.env once.",
    "",
  ].join("\n");

  output.write(prompt);

  const rl = readline.createInterface({ input, output });
  const applicationId = (await rl.question("Discord Application ID: ")).trim();
  rl.close();

  if (!applicationId) {
    throw new Error("A Discord Application ID is required to use Rich Presence.");
  }

  const validationResult = discordApplicationIdSchema.safeParse(applicationId);
  if (!validationResult.success) {
    throw new Error(validationResult.error.issues[0]?.message ?? "Discord Application ID is invalid.");
  }

  const envContent = await readFile(envPath, "utf8");
  const updatedEnvContent = envContent.match(/^DISCORD_APPLICATION_ID=.*$/m)
    ? envContent.replace(/^DISCORD_APPLICATION_ID=.*$/m, `DISCORD_APPLICATION_ID=${validationResult.data}`)
    : `${envContent.trimEnd()}\nDISCORD_APPLICATION_ID=${validationResult.data}\n`;

  await writeFile(envPath, `${updatedEnvContent.trimEnd()}\n`, "utf8");
  process.env.DISCORD_APPLICATION_ID = validationResult.data;
}

function normalizeOptional(value: string | undefined): string | undefined {
  const trimmed = value?.trim();
  return trimmed ? trimmed : undefined;
}

function normalizeEnvValue(value: unknown): string | undefined {
  if (typeof value !== "string") {
    return undefined;
  }

  return normalizeOptional(value);
}

function formatError(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }

  return String(error);
}

function log(message: string): void {
  const timestamp = new Date().toLocaleTimeString();
  console.log(`[${timestamp}] ${message}`);
}
