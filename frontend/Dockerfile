# syntax=docker/dockerfile:1

# Stage 1: build the static bundle with Node. None of this ends up in the runtime image.
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY . .
RUN npm run build

# Stage 2: serve with the unprivileged Nginx image (runs as uid 101, listens on 8080).
FROM nginxinc/nginx-unprivileged:1.29-alpine
# Upstream for /api; Compose uses the service name, Helm points it at the backend Service.
ENV BACKEND_URL=http://backend:8000
# Pick up Alpine security fixes published after the base image was built.
USER root
RUN apk upgrade --no-cache
COPY nginx.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /app/dist /usr/share/nginx/html
USER 101
EXPOSE 8080
