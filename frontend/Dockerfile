# ── Build stage: compile the React app ───────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies first (better layer caching).
COPY package*.json ./
RUN npm ci

# Copy source and build.
COPY . .
RUN npm run build
# Output is in /app/dist


# ── Runtime stage: serve with nginx ───────────────────────────────────────────
FROM nginx:alpine

# Replace the default nginx config with ours (which proxies /api to backend).
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy the built React app from the builder stage.
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
