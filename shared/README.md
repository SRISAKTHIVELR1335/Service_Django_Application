# shared/ – Contracts, Schemas, Assets

This module centralizes API contracts, JSON schemas, and shared models
used by backend, Windows client, and Android client.

Structure:
- api-contracts/openapi.yaml         → OpenAPI definition of the backend API
- api-contracts/schemas/*.json      → JSON Schemas for core entities
- models-py/contracts.py            → Pydantic models aligned with schemas
- models-js/contracts.js            → JS contract maps for React Native app
- assets/                           → Shared images / diagrams
