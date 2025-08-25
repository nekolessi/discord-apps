import { REST, Routes, type RESTPostAPIApplicationCommandsJSONBody } from "discord.js";
import "dotenv/config";

// Import the same commands used by the bot at runtime (named exports)
import { echo } from "./commands/echo";
import { ping } from "./commands/ping";
import { help } from "./commands/help";

const token = process.env.DISCORD_TOKEN as string;
const appId = process.env.APP_ID as string;
const guildId = process.env.GUILD_ID as string | undefined;

if (!token || !appId) {
  throw new Error("Missing DISCORD_TOKEN or APP_ID");
}

const commands = [echo, ping, help];
const body: RESTPostAPIApplicationCommandsJSONBody[] = commands.map((c) => c.data.toJSON());

const rest = new REST({ version: "10" }).setToken(token);

// Read --scope argument (guild|global), default to guild for fast iteration
const scopeFlagIndex = process.argv.indexOf("--scope");
const scope = scopeFlagIndex > -1 ? (process.argv[scopeFlagIndex + 1] ?? "guild") : "guild";

async function main(): Promise<void> {
  if (scope === "global") {
    console.log("[register] Registering GLOBAL commands…");
    await rest.put(Routes.applicationCommands(appId), { body });
    console.log("[register] Registered GLOBAL commands");
    return;
  }

  if (!guildId) {
    throw new Error("GUILD_ID is required for guild-scoped registration");
  }

  console.log(`[register] Registering GUILD (${guildId}) commands…`);
  await rest.put(Routes.applicationGuildCommands(appId, guildId), { body });
  console.log("[register] Registered GUILD commands");
}

main().catch((err) => {
  console.error("[register] failed:", err);
  process.exitCode = 1;
});
