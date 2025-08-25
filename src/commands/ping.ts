import { SlashCommandBuilder } from 'discord.js'
import type { SlashCommand } from '../types.js'


export const command: SlashCommand = {
data: new SlashCommandBuilder()
.setName('ping')
.setDescription('Replies with pong and latency'),
async execute(interaction) {
const sent = await interaction.reply({ content: 'Pinging…', fetchReply: true })
const latency = sent.createdTimestamp - interaction.createdTimestamp
await interaction.editReply(`Pong! Latency: ${latency}ms`)
}
}