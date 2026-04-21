# 🏁 Sprint 7 — Final Integration & QA

**Goal:** Final system hardening, end-to-end testing, and production readiness.

---

## 🛠️ Tasks

- [ ] **End-to-End (E2E) Testing**:
    - Build integration tests that simulate a full `Input -> Output` cycle including database persistence.
    - **Load Testing**: Verify PostgreSQL `jsonb` performance and orchestration throughput under concurrent loads.
- [ ] **Observability Hardening**:
    - Implement tracing to link logs to `context_id`.
    - Ensure PII is handled securely in snapshots.
- [ ] **Model Residency Optimization**:
    - Configure different models for different layers (e.g., Flash for Validation, reasoning model for Planning).
- [ ] **Final UX Polish**:
    - Ensure all status messages in the SSE stream are "calm" and descriptive.
- [ ] **Documentation Update**:
    - Update the project README with setup and deployment instructions.

---

## 📦 Definition of Done

- [ ] Full E2E test suite passes across all core business intents.
- [ ] Performance audit: Full orchestration completes in <10 seconds.
- [ ] PII audit: Verified that sensitive data is encrypted in the snapshots table.
