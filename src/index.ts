import { Client, GatewayIntentBits, Events, type Interaction } from "discord.js";
import "dotenv/config";
import type { SlashCommand } from "../types";
// import commands from src/commands
import { echo } from "./commands/echo";
import { ping } from "./commands/ping";
import { help } from "./commands/help";

const token = process.env.DISCORD_TOKEN as string;
if (!token) throw new Error("DISCORD_TOKEN is not set");

const commands: SlashCommand[] = [echo, ping, help];
const client = new Client({ intents: [GatewayIntentBits.Guilds] });

client.once(Events.ClientReady, (c) => {
  console.log(`[ready] Logged in as ${c.user.tag}`);
});

async function handleInteraction(interaction: Interaction): Promise<void> {
  try {
    if (!interaction.isChatInputCommand()) return;
    const cmd = commands.find((c) => c.data.name === interaction.commandName);
    if (!cmd) return;
    await cmd.execute(interaction);
  } catch (err) {
    console.error("[interaction] failed:", err);
    if (interaction.isRepliable()) {
      const content = "There was an error while executing this command.";
      if (interaction.deferred || interaction.replied) {
        await interaction.followUp({ content, ephemeral: true });
      } else {
        await interaction.reply({ content, ephemeral: true });
      }
    }
  }
}

client.on(Events.InteractionCreate, (interaction: Interaction) => {
  void handleInteraction(interaction);
});

await client.login(token);
