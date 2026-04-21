# 🟢 Sprint 0 — Baseline & Infrastructure

**Goal:** Establish the project foundation and initialize the persistent data layer.

---

## 🛠️ Tasks

- [ ] **Project Scaffolding**: 
    - Initialize Node.js/TypeScript environment (or preferred language).
    - Set up directory structure: `core/`, `api/`, `schemas/`, `tests/`.
- [ ] **Database Initialization**:
    - Set up PostgreSQL instance (local or containerized).
    - Executing the DDL from the `infrastructure_audit.md`.
    - **Initialize Migration Tool**: Set up Prisma, Drizzle, or Flyway to manage schema changes.
    - Verify table creation: `orchestrations`, `workflow_instances`, `context_snapshots`.
- [ ] **CI/CD & Linting**:
    - Set up ESLint/Prettier with "Uncle Bob" configuration.
    - Initialize basic test runner (Vitest/Jest).
- [ ] **Secrets Management**:
    - Create a `.env.example` defining placeholders for `OPENAI_API_KEY`, `POSTGRES_URL`, and integration tokens.

---

## 📦 Definition of Done

- [ ] Project builds with zero lint errors.
- [ ] Database connection test passes.
- [ ] Initial "Hello World" API endpoint is reachable.
