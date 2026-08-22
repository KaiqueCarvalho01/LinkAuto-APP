# Base Node.js image
FROM node:20-alpine AS base

WORKDIR /workspace

# Development stage with hot reload (Vite HMR)
FROM base AS development

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]

# Build stage for production artifact
FROM base AS build

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Production stage serving static assets via Nginx
FROM nginx:alpine AS production

COPY --from=build /workspace/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
