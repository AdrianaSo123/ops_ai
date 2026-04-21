# 📶 Sprint 6 — API Orchestration & SSE Streaming

**Goal:** Assemble the multi-stage pipeline and implement real-time status updates.

---

## 🛠️ Tasks

- [ ] **State Machine Assembly**:
    - Build the `Orchestrator` service that coordinates the linear flow between layers.
- [ ] **SSE Endpoint**:
    - Implement the `GET /api/orchestrate/:id/stream` endpoint.
    - Emit events for each stage transition (Interpretation, Planning, etc.).
    - **SSE Heartbeat**: Implement a keep-alive mechanism to prevent connection timeouts.
- [ ] **Human-in-the-loop (HITL) Logic**:
    - Implement the `PENDING_APPROVAL` logic.
    - Provide a "Review & Confirm" API endpoint.
- [ ] **Integration Stubbing**:
    - Create stubs for external Dispatch Services (Email, Slack, Jira).

---

## 📦 Definition of Done

- [ ] A browser client can listen to an SSE stream and see real-time updates as the orchestration progresses.
- [ ] High-stakes intents (e.g., Email) successfully enter `PENDING_APPROVAL` status.
