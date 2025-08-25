import { SlashCommandBuilder, EmbedBuilder } from 'discord.js'
import type { SlashCommand } from '../types.js'


export const command: SlashCommand = {
data: new SlashCommandBuilder().setName('help').setDescription('List commands'),
async execute(interaction) {
const embed = new EmbedBuilder()
.setTitle('Available Commands')
.setDescription('`/ping`, `/echo`, `/help`')
.setFooter({ text: 'Add more in src/commands' })
await interaction.reply({ embeds: [embed], ephemeral: true })
}
}