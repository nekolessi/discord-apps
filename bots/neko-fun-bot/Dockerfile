# syntax=docker/dockerfile:1
FROM node:20-alpine AS base
WORKDIR /repo
ENV PNPM_HOME=/pnpm
ENV PATH=$PNPM_HOME:$PATH
RUN corepack enable

FROM base AS deps
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY bots/neko-fun-bot/package.json bots/neko-fun-bot/package.json
RUN pnpm install --frozen-lockfile --filter ./bots/neko-fun-bot...

FROM deps AS build
COPY bots/neko-fun-bot bots/neko-fun-bot
RUN pnpm --filter ./bots/neko-fun-bot build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
RUN addgroup -S app && adduser -S bot -G app

COPY --from=deps /repo/node_modules /repo/node_modules
COPY --from=deps /repo/bots/neko-fun-bot/node_modules ./node_modules
COPY --from=build /repo/bots/neko-fun-bot/dist ./dist
COPY --from=build /repo/bots/neko-fun-bot/package.json ./package.json

USER bot
CMD ["node", "--enable-source-maps", "dist/src/index.js"]

