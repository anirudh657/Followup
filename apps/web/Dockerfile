# Dev-oriented Dockerfile for docker-compose. Production runs on Vercel, not this image.
FROM node:20-alpine
WORKDIR /app
RUN corepack enable
COPY package.json pnpm-lock.yaml* ./
RUN pnpm install
COPY . .
EXPOSE 3000
CMD ["pnpm", "dev"]
