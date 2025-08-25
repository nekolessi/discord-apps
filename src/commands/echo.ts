import { SlashCommandBuilder } from 'discord.js'
import type { SlashCommand } from '../types.js'


export const command: SlashCommand = {
data: new SlashCommandBuilder()
.setName('echo')
.setDescription('Echo back your message')
.addStringOption(opt =>
opt.setName('text').setDescription('What should I say?').setRequired(true)
),
async execute(interaction) {
const text = interaction.options.getString('text', true)
await interaction.reply({ content: text, ephemeral: false })
}
}