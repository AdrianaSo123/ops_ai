# 🔵 Sprint 1 — Base Driver Architecture

**Goal:** Establish the formal contract and registry for external integrations.

---

## 🛠️ Tasks

- [ ] **Driver Foundation**:
    - Implement `BaseDriver` (ABC) in `opsai/core/drivers/base.py`.
    - Include `check_health()` and `execute(payload)` methods.
- [ ] **Driver Registry**:
    - Implement `DriverRegistry` in `opsai/core/drivers/registry.py`.
    - Support dynamic registration of drivers via `StepType`.
    - Implement the `ENABLED` toggle logic (fallback to `MockDriver`).
- [ ] **Health Check Framework**:
    - Add a global `driver_startup_check()` to the application startup life cycle in `main.py`.

---

## 📦 Definition of Done

- [ ] `Registry` correctly returns `MockDriver` when a specific driver is disabled in `.env`.
- [ ] `check_health()` is called for all registered drivers on startup.
- [ ] Base tests for the Registry verify correct routing.
