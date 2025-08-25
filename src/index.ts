import { Client, GatewayIntentBits, Events, type Interaction } from 'discord.js';
import 'dotenv/config';
import { logger } from './logger.js';
import type { SlashCommand } from './types.js';
import { commands } from './register.js'; // assuming register.ts exports an array of commands


const token = process.env.DISCORD_TOKEN as string;
if (!token) {
throw new Error('DISCORD_TOKEN is not set');
}


const client = new Client({ intents: [GatewayIntentBits.Guilds] });


client.once(Events.ClientReady, (c) => {
logger.info({ user: c.user.tag }, 'Bot is ready');
});


// Typed handler to satisfy no-explicit-any and no-misused-promises
async function handleInteraction(interaction: Interaction): Promise<void> {
try {
if (!interaction.isChatInputCommand()) return;
const cmd = (commands as SlashCommand[]).find(
(c) => c.data.name === interaction.commandName
);
if (!cmd) return;
await cmd.execute(interaction);
} catch (err) {
logger.error({ err }, 'Interaction handler failed');
if (interaction.isRepliable()) {
const content = 'There was an error while executing this command.';
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