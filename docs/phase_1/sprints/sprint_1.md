# 🔵 Sprint 1 — Interpretation Layer & Intent Mapping

**Goal:** Transform raw text into structured intents and initial entities.

---

## 🛠️ Tasks

- [ ] **Intent Classifier Implementation**:
    - Implement the `Interpretation` layer using the `Classifier` pattern.
    - Map inputs to the `Intent` Enum defined in `spec.md`.
- [ ] **Initial Entity Extraction**:
    - Extract basic organization names and contacts from input strings.
- [ ] **Ambiguity & Out-of-Scope Detection**:
    - Implement logic to handle `AMBIGUOUS_INPUT` and `OUT_OF_SCOPE` intents.
- [ ] **State Machine Hook**:
    - Implement initial entry in the `orchestrations` table with `status = 'INTERPRETING'`.
    - Update to `status = 'PLANNING'` upon success.

---

## 📦 Definition of Done

- [ ] Unit tests for intent classification reach >90% accuracy for core intents.
- [ ] "Client Onboarding" input correctly parses to `CLIENT_ONBOARDING` intent.
- [ ] Integration test: Row created in `orchestrations` table.
