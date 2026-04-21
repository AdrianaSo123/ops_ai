# 🟣 Sprint 2 — Context Management & Snapshots

**Goal:** Implement the "Working Memory" of the system and persistent context snapshots.

---

## 🛠️ Tasks

- [ ] **Context Model**:
    - Implement the `Context` object as defined in `spec.md` Section 5.
- [ ] **Snapshoting Logic**:
    - Implement the `context_snapshots` database repository.
    - Store the `Context` state at the end of the Interpretation stage.
- [ ] **Immutable Context Pattern**:
    - Ensure context objects are passed by reference but treated as immutable snapshots during layer transitions.
- [ ] **Entity Persistence**:
    - Finalize parsing logic to populate `organization`, `contacts`, and `dates` in the context object.

---

## 📦 Definition of Done

- [ ] Successful write/read of a `context_snapshot` for a given `orchestration_id`.
- [ ] Entities extracted in Sprint 1 are verified as persistent in the database.
