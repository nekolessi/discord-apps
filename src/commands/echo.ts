import { SlashCommandBuilder, type ChatInputCommandInteraction } from "discord.js";
import type { SlashCommand } from "../types";

export const echo: SlashCommand = {
  data: new SlashCommandBuilder()
    .setName("echo")
    .setDescription("Echo back the provided text")
    .addStringOption((o) =>
      o.setName("text").setDescription("Text to echo").setRequired(true)
    ),
  async execute(interaction: ChatInputCommandInteraction) {
    const text = interaction.options.getString("text", true);
    await interaction.reply(text);
  },
};
