import { SlashCommandBuilder, type ChatInputCommandInteraction } from "discord.js";
import type { SlashCommand } from "../../types";

export const help: SlashCommand = {
  data: new SlashCommandBuilder()
    .setName("help")
    .setDescription("List available commands"),
  async execute(interaction: ChatInputCommandInteraction) {
    const lines = [
      "**Available commands:**",
      "• `/ping` – reply with Pong and latency",
      "• `/echo text:<message>` – echo your message",
      "• `/help` – show this list",
    ];
    await interaction.reply(lines.join("\n"));
  },
};
