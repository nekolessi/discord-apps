import "dotenv/config";
import { z } from "zod";

const RawEnvSchema = z.object({
  DISCORD_TOKEN: z.string().min(1),
  DISCORD_CLIENT_ID: z.string().optional(),
  DISCORD_GUILD_ID: z.string().optional(),
  APP_ID: z.string().optional(),
  GUILD_ID: z.string().optional(),
  NODE_ENV: z.string().default("development"),
  LOG_PRETTY: z.string().optional(),
  LOG_LEVEL: z.string().optional(),
});

const rawEnv = RawEnvSchema.parse(process.env);

export const env = {
  ...rawEnv,
  DISCORD_CLIENT_ID: rawEnv.DISCORD_CLIENT_ID ?? rawEnv.APP_ID,
  DISCORD_GUILD_ID: rawEnv.DISCORD_GUILD_ID ?? rawEnv.GUILD_ID,
};
