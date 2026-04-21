# 🔵 Sprint 4 — Resilient Dispatcher & Global Toggle

**Goal:** Integrate the real drivers into the core execution pipeline with enhanced error handling and toggles.

---

## 🛠️ Tasks

- [ ] **Dispatcher Refactoring**:
    - Update the `Dispatcher` loop to call the `DriverRegistry`.
    - Implement the **Exponential Backoff** logic for steps where `result['is_recoverable']` is `True`.
- [ ] **Mock/Real Toggle**:
    - Implement a global `OPSAI_LIVE_MODE` flag in `.env` or rely on the per-driver `ENABLED` flags to swap implementations.
- [ ] **End-to-End Live Verification**:
    - Build a `test_live_integrations.py` script to verify the entire flow from Planning to Real-World execution.

---

## 📦 Definition of Done

- [ ] Successful completion of an HR Onboarding flow sending a real (live) email and creating a real (live) Linear task.
- [ ] Verified that disabling a key in `.env` correctly falls back to the Mock provider without crashing the system.
- [ ] Documentation updated in `README.md` for Integration setup.
