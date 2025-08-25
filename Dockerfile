# ------- base with pnpm cache
FROM node:20-alpine AS base
ENV PNPM_HOME=/pnpm
ENV PATH=$PNPM_HOME:$PATH
RUN corepack enable
WORKDIR /app


# ------- prod deps (no dev)
FROM base AS prod-deps
COPY package.json pnpm-lock.yaml* ./
RUN pnpm install --frozen-lockfile --prod


# ------- build
FROM base AS build
COPY package.json pnpm-lock.yaml* ./
RUN pnpm install --frozen-lockfile
COPY tsconfig.json tsconfig.build.json ./
COPY src ./src
RUN pnpm build


# ------- runner
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
# non-root user
RUN addgroup -S app && adduser -S bot -G app
COPY --from=prod-deps /app/node_modules ./node_modules
COPY --from=build /app/dist ./dist
COPY package.json ./package.json
USER bot
CMD ["node", "--enable-source-maps", "dist/index.js"]
