# 🔵 Sprint 3 — Linear Integration

**Goal:** Implement actual task creation using the Linear GraphQL API.

---

## 🛠️ Tasks

- [ ] **Linear Driver Implementation**:
    - Build `LinearDriver` in `opsai/core/drivers/task_creation/linear.py`.
    - Implement GraphQL queries/mutations using `httpx`.
- [ ] **Error Mapping**:
    - Implement logic to map Linear API response codes to the `is_recoverable` status.
- [ ] **Payload Mapping**:
    - Map AI `TASK_CREATION` fields to Linear Team IDs and Project IDs defined in configuration.
- [ ] **Configuration**:
    - Add `OPSAI_DRIVER_LINEAR_KEY` and `OPSAI_DRIVER_LINEAR_TEAM_ID` to `.env`.

---

## 📦 Definition of Done

- [ ] `check_health()` successfully queries the Linear API for the provided team.
- [ ] Test task created successfully in a Linear inbox.
- [ ] API timeouts are correctly marked as `is_recoverable = True`.
