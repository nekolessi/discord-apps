// register.ts (at repo root)
import 'dotenv/config';
import { REST, Routes } from 'discord.js';

// ✅ Import from src/, no file extensions
import { ping } from './src/commands/ping';
import { echo } from './src/commands/echo';
import { help } from './src/commands/help';

const token = process.env.DISCORD_TOKEN as string;
const clientId = process.env.DISCORD_CLIENT_ID as string;
const guildId = process.env.DISCORD_GUILD_ID as string;

if (!token) throw new Error('DISCORD_TOKEN is not set');
if (!clientId) throw new Error('DISCORD_CLIENT_ID is not set');

const rest = new REST({ version: '10' }).setToken(token);

// Collect command JSON
const commands = [ping, echo, help].map((c) => c.data.toJSON());

// Read scope from CLI flag: --scope guild|global
const scopeFlagIndex = process.argv.indexOf('--scope');
const scope =
  scopeFlagIndex !== -1 && process.argv[scopeFlagIndex + 1]
    ? process.argv[scopeFlagIndex + 1]
    : 'guild';

async function main() {
  if (scope === 'global') {
    console.log('[register] Registering GLOBAL application commands…');
    await rest.put(Routes.applicationCommands(clientId), { body: commands });
    console.log('[register] Global commands upserted.');
  } else {
    if (!guildId) throw new Error('DISCORD_GUILD_ID is not set for guild scope');
    console.log(`[register] Registering GUILD commands to ${guildId}…`);
    await rest.put(Routes.applicationGuildCommands(clientId, guildId), {
      body: commands,
    });
    console.log('[register] Guild commands upserted.');
  }
}

main().catch((err) => {
  console.error('[register] failed:', err);
  process.exit(1);
});
