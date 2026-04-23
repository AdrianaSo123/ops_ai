# Phase 4 — Sprint 1: Conditional Logic & Execution Flow

## Goals
- Implement conditional branching for workflow steps
- Update execution flow to support dynamic next steps
- Update Step and StepStatus models as per spec

## Tasks
- [ ] Update `Step` model to include `on_success`, `on_failure`, and `conditions`
- [ ] Update `StepStatus` model to include `retries`
- [ ] Implement conditional branching logic in `decision_engine.py`
- [ ] Update `executor.py` to call decision engine after each step
- [ ] Add/Update unit tests for conditional logic and branching

## Acceptance Criteria
- Steps can branch to different next steps based on result
- Step status and retry count are tracked
- All new logic is covered by unit tests
