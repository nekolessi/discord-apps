import { SlashCommandBuilder, type ChatInputCommandInteraction } from "discord.js";
import type { SlashCommand } from "../../types";

export const ping: SlashCommand = {
  data: new SlashCommandBuilder()
    .setName("ping")
    .setDescription("Replies with Pong! and latency"),
  async execute(interaction: ChatInputCommandInteraction) {
    const sent = await interaction.reply({ content: "Pong!", fetchReply: true });
    const latency = sent.createdTimestamp - interaction.createdTimestamp;
    await interaction.followUp(`Latency: ${latency}ms`);
  },
};
