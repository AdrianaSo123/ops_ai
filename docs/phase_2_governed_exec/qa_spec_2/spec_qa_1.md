# 🔍 QA Analysis: Phase 2 Specification (Iteration 1)

**Phase:** Phase 2 (Governed Execution Engine)  
**Document:** [spec.md](file:///Users/adrianaso/opsAI/docs/phase_2_governed_exec/spec.md)  
**QA Iteration:** 1  

---

## 🏛️ Architectural Integrity

### 1. State Machine Completeness
> [!WARNING]
> **Issue:** The lifecycle stops at `COMPLETED | FAILED` at the orchestration level, but the **failure recovery path** is undefined.
> 
> **Gap:** If a workflow has 5 steps and fails at step 3:
> - Does the system allow re-running just the failed step?
> - Does an "Approve" action on a `FAILED` orchestration restart from the beginning or resume?
> 
> **Recommendation:** Define a `RESUME` or `RETRY` logic for orchestrations that fail mid-execution.

### 2. The "Payload Generation" Timing
> [!IMPORTANT]
> **Issue:** Payloads are generated *before* `PENDING_APPROVAL`, but the context might change while waiting for a human.
> 
> **Risk:** If a human takes 24 hours to approve a "Send Follow-up" email, the specific data (like a date or price mentioned in the draft) might be stale.
> 
> **Recommendation:** Ensure payloads are **validated** again immediately upon approval, OR allow the human to **Edit** the payload as part of the approval process.

---

## 📦 Data Modeling

### 1. Step vs. StepStatus decoupling
> [!NOTE]
> **Observation:** Separating `Step` (the command) from `StepStatus` (the result) is excellent for clean code.
> 
> **Refinement:** In a production-grade system, each `StepStatus` should include a `start_time` and `end_time` to enable latency tracking (Observability).

### 2. Missing "Snapshot" Integration
> [!CAUTION]
> **Omission:** The Phase 2 spec doesn't explicitly mention the **Context Snapshots** established in Phase 1.
> 
> **Risk:** We must ensure that the `Dispatcher` takes a snapshot of the context *before* and *after* every step is executed to maintain the "System of Record" standard.

---

## 📡 API & Governance

### 1. Approval Flexibility
> [!WARNING]
> **Issue:** The only action is `POST /approve`. 
> 
> **Gap:** There is no explicit `REJECT` or `CANCEL` endpoint. Without this, a bad plan stays in `PENDING_APPROVAL` indefinitely or must be manually deleted from the DB.
> 
> **Recommendation:** Add `POST /api/orchestrations/{id}/reject`.

### 2. Integration Safety (Pii)
> [!IMPORTANT]
> **Risk:** Execution (Dispatcher) involves sending data to "Email" and "Task" mocks. 
> 
> **Requirement:** The spec should distinguish between **Structural Validation** (is the JSON correct?) and **Semantic Validation** (is the email address valid/safe?).

---

## 🏁 Summary Conclusion
**Current Grade: 8/10**

The spec is highly actionable and logically follows Phase 1. However, the **Failure/Retry logic** and the **Lack of a "Reject" state** are the primary blockers to a production-ready governance model. 

**Next Action:** Refine the spec to address the "Reject" state and "Resumption" logic.
