# Use Node 20 LTS
FROM node:20-alpine AS base
WORKDIR /app


# Install deps separately for better layer caching
COPY package.json pnpm-lock.yaml* yarn.lock* package-lock.json* ./


# Use pnpm if available, fall back to npm
RUN if [ -f pnpm-lock.yaml ]; then npm i -g pnpm && pnpm i --frozen-lockfile; \
elif [ -f yarn.lock ]; then yarn install --frozen-lockfile; \
else npm ci; fi


COPY tsconfig.json ./
COPY src ./src


RUN npm run build || yarn build || pnpm build


# Runtime image
FROM node:20-alpine
WORKDIR /app
ENV NODE_ENV=production


COPY --from=base /app/package.json ./
COPY --from=base /app/node_modules ./node_modules
COPY --from=base /app/dist ./dist


CMD ["node", "dist/index.js"]