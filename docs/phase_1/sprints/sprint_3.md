# 🟡 Sprint 3 — Planning Layer & Workflow Strategy

**Goal:** Translate intents and context into a multi-step execution plan.

---

## 🛠️ Tasks

- [ ] **Strategy Generator**:
    - Implement the `Planning` layer using the `Strategy` pattern.
    - Generate a list of workflow steps based on the `Intent`.
- [ ] **Step Type Mapping**:
    - Ensure steps use the `StepType` Enum: `COMMUNICATION`, `COORDINATION`, `TASK_CREATION`.
- [ ] **Workflow Persistence**:
    - Save the generated plan to the `workflow_instances` table.
- [ ] **State Machine Update**:
    - Transition orchestration status from `PLANNING` to `EXECUTING`.

---

## 📦 Definition of Done

- [ ] A `CLIENT_ONBOARDING` intent produces a workflow with at least 3 distinct steps (Communication, Meeting, Task).
- [ ] Workflow steps are verified as stored in `workflow_instances`.
