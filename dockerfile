FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files for installation
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Truyền các biến môi trường khi build
ARG NEXT_PUBLIC_API_BASE_URL
ARG NEXT_FRONTEND_URL
ARG NEXT_BACKEND_URL
ARG NEXT_HOCTIEP_URL
ARG NEXT_HOCTIEP_KEY
ARG NEXT_METABASE_INSTANCE_URL
ARG NEXTAUTH_URL
ARG AUTH_SECRET
ARG GOOGLE_CLIENT_ID
ARG GOOGLE_CLIENT_SECRET

# Set các biến môi trường cho quá trình build
ENV NEXT_PUBLIC_API_BASE_URL=$NEXT_PUBLIC_API_BASE_URL
ENV NEXT_FRONTEND_URL=$NEXT_FRONTEND_URL
ENV NEXT_BACKEND_URL=$NEXT_BACKEND_URL
ENV NEXT_HOCTIEP_URL=$NEXT_HOCTIEP_URL
ENV NEXT_HOCTIEP_KEY=$NEXT_HOCTIEP_KEY
ENV NEXT_METABASE_INSTANCE_URL=$NEXT_METABASE_INSTANCE_URL
ENV NEXTAUTH_URL=$NEXTAUTH_URL
ENV AUTH_SECRET=$AUTH_SECRET
ENV GOOGLE_CLIENT_ID=$GOOGLE_CLIENT_ID
ENV GOOGLE_CLIENT_SECRET=$GOOGLE_CLIENT_SECRET

# Disable telemetry
ENV NEXT_TELEMETRY_DISABLED=1

# Build ứng dụng
RUN npm run build || (echo "❌ BUILD FAILED" && exit 1)

# Production image
FROM node:20-alpine AS production

WORKDIR /app

# Set production environment
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Tăng cường bảo mật bằng cách tạo user không có quyền root
# RUN addgroup --system --gid 1001 nodejs
# RUN adduser --system --uid 1001 nextjs

# Copy các file cần thiết từ builder
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/next.config.ts ./next.config.ts

# Thiết lập các biến môi trường runtime
ENV NEXT_PUBLIC_API_BASE_URL=$NEXT_PUBLIC_API_BASE_URL
ENV NEXT_FRONTEND_URL=$NEXT_FRONTEND_URL
ENV NEXT_BACKEND_URL=$NEXT_BACKEND_URL
ENV NEXT_HOCTIEP_URL=$NEXT_HOCTIEP_URL
ENV NEXT_HOCTIEP_KEY=$NEXT_HOCTIEP_KEY
ENV NEXT_METABASE_INSTANCE_URL=$NEXT_METABASE_INSTANCE_URL
ENV NEXTAUTH_URL=$NEXTAUTH_URL
ENV AUTH_SECRET=$AUTH_SECRET
ENV GOOGLE_CLIENT_ID=$GOOGLE_CLIENT_ID
ENV GOOGLE_CLIENT_SECRET=$GOOGLE_CLIENT_SECRET

# Phân quyền cho thư mục ứng dụng
# RUN chown -R nextjs:nodejs /app

# # Chuyển sang user không phải root
# USER nextjs

EXPOSE 3000

CMD ["npm", "start"]
