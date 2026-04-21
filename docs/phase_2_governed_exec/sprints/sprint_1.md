# 🔵 Sprint 1 — Orchestration State & Advanced Models

**Goal:** Expand the data model to support governance, multi-tenancy, and granular step tracking.

---

## 🛠️ Tasks

- [ ] **Multi-Tenant Foundation**:
    - Add `organization_id` (UUID) and `user_id` (UUID) fields to the `Orchestration` model.
    - Ensure these fields are mandatory for every new orchestration.
- [ ] **Governance Lifecycle Expansion**:
    - Add `REJECTED` and `CANCELLED` statuses to the `OrchestrationStatus` Enum.
    - Implement `updated_at` logic using SQLModel listeners or manual updates in `ContextManager`.
- [ ] **Granular Step Tracking**:
    - Implement the `StepStatus` model (as defined in `spec.md`).
    - Create a one-to-many relationship between `Orchestration` and `StepStatus`.
- [ ] **Database Migration**:
    - Re-initialize or migrate the SQLite schema to include these new fields and tables.
    - **Note:** For development, perform a `DROP TABLE` or delete `opsai.db` to ensure schema consistency.

---

## 📦 Definition of Done

- [ ] `Orchestration` model updated and verified via unit tests.
- [ ] `StepStatus` objects can be created and linked to an orchestration.
- [ ] Validated that `organization_id` is required for record creation.
