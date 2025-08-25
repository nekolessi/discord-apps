import pino from 'pino'
import { env } from './env.js'


export const logger = pino({
level: env.NODE_ENV === 'production' ? 'info' : 'debug',
transport:
env.LOG_PRETTY === 'true' || env.NODE_ENV !== 'production'
? { target: 'pino-pretty', options: { colorize: true } }
: undefined
})