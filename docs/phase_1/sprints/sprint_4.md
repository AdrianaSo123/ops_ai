# 🟠 Sprint 4 — Execution & Structured Payloads

**Goal:** Convert abstract workflow steps into concrete, system-ready payloads.

---

## 🛠️ Tasks

- [ ] **Payload Generator Implementation**:
    - Implement the `Execution` layer using the `Command` pattern.
- [ ] **Template Mapping**:
    - Build JSON templates for Emails, Tasks, and Calendar Events.
    - Hydrate templates using data from the `Context` (e.g., `client_name`).
    - **Nullable Data Strategy**: Implement fallbacks (e.g., "valued client") for missing context entities.
- [ ] **Integration Logic**:
    - For each `StepType`, generate the specific payload required for the target integration (e.g., Jira-compatible JSON).
- [ ] **Immutable Results**:
    - Store the generated results in the orchestration's final stage memory.

---

## 📦 Definition of Done

- [ ] Execution layer generates valid JSON payloads for each step in a standard onboarding workflow.
- [ ] Manual check verifies that `client_name` is correctly injected into the "Onboarding Email" payload.
