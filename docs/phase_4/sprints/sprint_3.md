# Phase 4 — Sprint 3: Persistence & Resume

## Goals
- Implement persistent storage for workflow state (SQLite or JSON)
- Enable workflow resume from failure or paused state
- Update orchestrator and CLI to support resume command

## Tasks
- [ ] Implement `persistence.py` for save/load state
- [ ] Integrate persistence into workflow execution (save after every transition)
- [ ] Update orchestrator to support resume from any step
- [ ] Add CLI command for `resume <workflow_id>`
- [ ] Add/Update unit tests for persistence and resume logic

## Acceptance Criteria
- Workflow state is persisted after every transition
- System can resume from failure or paused state
- CLI resume command works as documented
- All new logic is covered by unit tests
