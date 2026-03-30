#!/usr/bin/env bash
set -e

echo "[NIRIX] Building backend Docker image..."
docker build -f ops/docker/backend.dockerfile -t nirix-backend .

echo "[NIRIX] Building nginx Docker image..."
docker build -f ops/docker/nginx.dockerfile -t nirix-nginx .

echo "[NIRIX] Starting services via docker-compose..."
docker compose up -d
