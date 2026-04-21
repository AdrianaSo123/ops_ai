# 🔵 Sprint 2 — Approval System & Governance API

**Goal:** Implement the "Pause" logic and necessary API endpoints for human oversight.

---

## 🛠️ Tasks

- [ ] **The "Pause" Implementation**:
    - Update the `Orchestrator` run loop to stop immediately after the `PLANNING` and `VALIDATING` stages.
    - Set the final status to `PENDING_APPROVAL`.
- [ ] **Approval Endpoint**:
    - Implement `POST /api/orchestrate/{id}/approve`.
    - This endpoint must:
        1. Validate the orchestration exists and is in `PENDING_APPROVAL`.
        2. Perform a "Staleness Check" (**re-run the `ValidationService`** to check if context and workflow still align).
        3. Trigger the `Dispatcher` in the background (using **FastAPI `BackgroundTasks`**).
- [ ] **Mock Dispatcher Interface**:
    - Define the `Dispatcher` class interface in `opsai/core/dispatcher.py` with a mock `run` method that just logs execution.
- [ ] **Rejection Endpoint**:
    - Implement `POST /api/orchestrate/{id}/reject`.
    - This endpoint must set the status to `REJECTED` and log the rejection event.
- [ ] **API Security (Basic)**:
    - Ensure that actions can only be performed if the orchestration is in the correct state.

---

## 📦 Definition of Done

- [ ] `POST /approve` successfully moves an orchestration to `EXECUTING`.
- [ ] `POST /reject` successfully moves an orchestration to `REJECTED`.
- [ ] "Staleness Check" correctly fails if the plan is no longer valid.
