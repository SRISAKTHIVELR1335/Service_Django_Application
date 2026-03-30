# Deployment Guide – NIRIX Diagnostics

High-level deployment steps:
1. Provision MySQL and create `nirix_diagnostics` database.
2. Configure `DATABASE_URL` for backend (`mysql+pymysql://...`).
3. Build backend and nginx Docker images from `ops/docker/`.
4. Start services using `docker compose` and the provided scripts.
5. Configure domain and TLS in nginx.
