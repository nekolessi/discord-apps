import { REST, Routes, SlashCommandBuilder } from 'discord.js'
import { env } from './utils/env.js'
import { logger } from './utils/logger.js'


// Import commands
import { command as ping } from './commands/ping.js'
import { command as echo } from './commands/echo.js'
import { command as help } from './commands/help.js'


const commandData = [ping, echo, help].map(c => c.data.toJSON())


const scope = process.argv.includes('--scope')
? process.argv[process.argv.indexOf('--scope') + 1]
: 'guild'


async function register() {
if (!env.DISCORD_TOKEN) throw new Error('Missing DISCORD_TOKEN')
const rest = new REST({ version: '10' }).setToken(env.DISCORD_TOKEN)


if (scope === 'global') {
if (!env.APP_ID) throw new Error('APP_ID required for global registration')
logger.info('Registering GLOBAL commands…')
await rest.put(Routes.applicationCommands(env.APP_ID), { body: commandData })
logger.info('Global commands registered')
} else {
if (!env.APP_ID || !env.GUILD_ID)
throw new Error('APP_ID and GUILD_ID required for guild registration')
logger.info({ guild: env.GUILD_ID }, 'Registering GUILD commands…')
await rest.put(Routes.applicationGuildCommands(env.APP_ID, env.GUILD_ID), {
body: commandData
})
logger.info('Guild commands registered')
}
}


register().catch(err => {
logger.error({ err }, 'Failed to register commands')
process.exit(1)
})