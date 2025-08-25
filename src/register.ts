import { REST, Routes, type RESTPostAPIApplicationCommandsJSONBody } from 'discord.js';
import 'dotenv/config';
import { logger } from './logger.js';
import { echo } from './echo.js';
import { ping } from './ping.js';
import { help } from './help.js';


// Export an array of commands so index.ts can discover them
export const commands = [echo, ping, help];


const token = process.env.DISCORD_TOKEN as string;
const appId = process.env.APP_ID as string;
const guildId = process.env.GUILD_ID as string | undefined;


if (!token || !appId) {
throw new Error('Missing DISCORD_TOKEN or APP_ID');
}


const rest = new REST({ version: '10' }).setToken(token);


const body: RESTPostAPIApplicationCommandsJSONBody[] = commands.map((c) => c.data.toJSON());


const scope = process.argv.includes('--scope') ? process.argv[process.argv.indexOf('--scope') + 1] : 'guild';


async function main() {
if (scope === 'global') {
logger.info('Registering GLOBAL commands…');
await rest.put(Routes.applicationCommands(appId), { body });
logger.info('Registered GLOBAL commands');
} else {
if (!guildId) throw new Error('GUILD_ID is required for guild scoped registration');
logger.info({ guildId }, 'Registering GUILD commands…');
await rest.put(Routes.applicationGuildCommands(appId, guildId), { body });
logger.info('Registered GUILD commands');
}
}


main().catch((err) => {
logger.error({ err }, 'Failed to register commands');
process.exitCode = 1;
});