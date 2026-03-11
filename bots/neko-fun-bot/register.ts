import "dotenv/config";
import { REST, Routes } from "discord.js";

import { echo } from "./src/commands/echo";
import { help } from "./src/commands/help";
import { ping } from "./src/commands/ping";

const token = process.env.DISCORD_TOKEN as string;
const clientId = process.env.DISCORD_CLIENT_ID as string;
const guildId = process.env.DISCORD_GUILD_ID as string;

if (!token) throw new Error("DISCORD_TOKEN is not set");
if (!clientId) throw new Error("DISCORD_CLIENT_ID is not set");

const rest = new REST({ version: "10" }).setToken(token);
const commands = [ping, echo, help].map((command) => command.data.toJSON());

const scopeFlagIndex = process.argv.indexOf("--scope");
const scope =
  scopeFlagIndex !== -1 && process.argv[scopeFlagIndex + 1]
    ? process.argv[scopeFlagIndex + 1]
    : "guild";

async function main(): Promise<void> {
  if (scope === "global") {
    console.log("[register] Registering GLOBAL application commands...");
    await rest.put(Routes.applicationCommands(clientId), { body: commands });
    console.log("[register] Global commands upserted.");
    return;
  }

  if (!guildId) throw new Error("DISCORD_GUILD_ID is not set for guild scope");

  console.log(`[register] Registering GUILD commands to ${guildId}...`);
  await rest.put(Routes.applicationGuildCommands(clientId, guildId), {
    body: commands,
  });
  console.log("[register] Guild commands upserted.");
}

main().catch((err) => {
  console.error("[register] failed:", err);
  process.exit(1);
});
