# 🔵 Sprint 3 — Dispatcher & Execution Engine

**Goal:** Build the robust execution engine that converts payloads into simulated real-world actions.

---

## 🛠️ Tasks

- [ ] **Dispatcher Service Foundation**:
    - Implement the `Dispatcher` class in `opsai/core/dispatcher.py`.
    - Implement a `run(orchestration)` method that iterates through workflow steps.
- [ ] **Resilient Execution Loop**:
    - Implement a retry loop for each step (`MAX_RETRIES = 3`).
    - Integrate mandatory `snapshot_context` calls before and after every single step to maintain the "System of Record."
- [ ] **Mock Service Providers**:
    - Build `EmailProvider` mock: Simulate sending emails.
    - Build `TaskProvider` mock: Simulate Jira/Linear ticket creation.
    - Build `CalendarProvider` mock: Simulate scheduling meetings.
- [ ] **State Updates**:
    - Update the `StepStatus` in the database for every attempt and result.

---

## 📦 Definition of Done

- [ ] `Dispatcher` successfully executes a 3-step workflow.
- [ ] Failures correctly trigger up to 3 retries.
- [ ] Success/Failure of individual steps is recorded and visible in the `StepStatus` table.
