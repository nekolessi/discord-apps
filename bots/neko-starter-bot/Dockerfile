# syntax=docker/dockerfile:1
FROM node:20-alpine AS base
WORKDIR /repo
ENV PNPM_HOME=/pnpm
ENV PATH=$PNPM_HOME:$PATH
RUN corepack enable

FROM base AS deps
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY bots/neko-starter-bot/package.json bots/neko-starter-bot/package.json
RUN pnpm install --frozen-lockfile --filter ./bots/neko-starter-bot...

FROM deps AS build
COPY bots/neko-starter-bot bots/neko-starter-bot
RUN pnpm --filter ./bots/neko-starter-bot build

FROM node:20-alpine AS runner
WORKDIR /repo/bots/neko-starter-bot
ENV NODE_ENV=production
RUN addgroup -S app && adduser -S bot -G app

COPY --from=deps /repo/node_modules /repo/node_modules
COPY --from=deps /repo/bots/neko-starter-bot/node_modules /repo/bots/neko-starter-bot/node_modules
COPY --from=build /repo/bots/neko-starter-bot/dist ./dist
COPY --from=build /repo/bots/neko-starter-bot/package.json ./package.json

USER bot
CMD ["node", "--enable-source-maps", "dist/src/index.js"]
