# Base Node.js image (same major version as CI)
FROM node:26-alpine AS base

WORKDIR /workspace

# Development stage with hot reload (Vite HMR)
FROM base AS development

COPY package*.json ./
# Reproducible installs from the lockfile
RUN npm ci

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]

# Build stage for production artifact
FROM base AS build

# The API URL is baked into the bundle at build time and must be given explicitly, e.g.
# docker build --target production --build-arg VITE_API_BASE_URL=https://api.example.com/api/v1
# (without it the bundle would silently call http://localhost:8000)
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
RUN test -n "$VITE_API_BASE_URL" || \
    (echo "Set --build-arg VITE_API_BASE_URL to the public API URL" >&2 && exit 1)

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Production stage serving the SPA via unprivileged Nginx (port 8080)
FROM nginxinc/nginx-unprivileged:stable-alpine AS production

COPY --chmod=644 nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /workspace/dist /usr/share/nginx/html

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD wget -q -O /dev/null http://127.0.0.1:8080/health || exit 1

CMD ["nginx", "-g", "daemon off;"]
