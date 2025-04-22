FROM node:20-alpine AS builder

WORKDIR /app

# Copy file cấu hình và env
COPY package*.json ./
COPY .env .env

# Cài đặt dependencies
RUN npm install

# Copy toàn bộ source code
COPY . .

# Disable telemetry
ENV NEXT_TELEMETRY_DISABLED=1

# Build ứng dụng
RUN npm run build || (echo "❌ BUILD FAILED" && exit 1)

# Production image
FROM node:20-alpine AS production

WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
# Cài các production dependencies
# COPY package*.json ./
# RUN npm install --omit=dev

# RUN addgroup --system --gid 1001 nodejs
# RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/next.config.ts ./next.config.ts
COPY --from=builder /app/.env ./.env

# RUN chown -R nextjs:nodejs /app
# USER nextjs

EXPOSE 3000

CMD ["npm", "start"]
