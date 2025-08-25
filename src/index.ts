import { Client, Collection, Events, GatewayIntentBits, REST, Routes } from 'discord.js'
import { env } from './utils/env.js'
import { logger } from './utils/logger.js'
import type { SlashCommand } from './types.js'


// Dynamically import all commands
import { command as ping } from './commands/ping.js'
import { command as echo } from './commands/echo.js'
import { command as help } from './commands/help.js'


const commands = new Collection<string, SlashCommand>()
for (const cmd of [ping, echo, help]) {
commands.set(cmd.data.name, cmd)
}


const client = new Client({ intents: [GatewayIntentBits.Guilds] })


client.once(Events.ClientReady, c => {
logger.info({ user: c.user.tag }, 'Bot is ready')
})


client.on(Events.InteractionCreate, async interaction => {
if (!interaction.isChatInputCommand()) return
const cmd = commands.get(interaction.commandName)
if (!cmd) {
await interaction.reply({ content: 'Unknown command', ephemeral: true })
return
}
try {
await cmd.execute(interaction)
} catch (err) {
logger.error({ err }, 'Command failed')
const content = 'There was an error while executing this command.'
if (interaction.deferred || interaction.replied) {
await interaction.editReply({ content })
} else {
await interaction.reply({ content, ephemeral: true })
}
}
})


async function main() {
if (!env.DISCORD_TOKEN) throw new Error('Missing DISCORD_TOKEN')
await client.login(env.DISCORD_TOKEN)
}


main().catch(err => {
logger.error({ err }, 'Fatal startup error')
process.exit(1)
})