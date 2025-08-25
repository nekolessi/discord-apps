import 'dotenv/config'
import { z } from 'zod'


const EnvSchema = z.object({
DISCORD_TOKEN: z.string().min(1),
APP_ID: z.string().optional(),
GUILD_ID: z.string().optional(),
NODE_ENV: z.string().default('development'),
LOG_PRETTY: z.string().optional()
})


export const env = EnvSchema.parse(process.env)