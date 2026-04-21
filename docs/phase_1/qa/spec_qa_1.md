# 🔍 OpsAI — System Spec QA Analysis (Iteration 1)

**Date:** 2026-04-20
**Target:** [spec.md](file:///Users/adrianaso/opsAI/docs/spec.md)  
**Status:** ✅ Review Completed

---

## 🏗️ Architectural Integrity

### The Orchestration Pipeline
The 4-stage pipeline (**Interpretation → Planning → Execution → Validation**) is a robust pattern for AI-first systems. It mirrors the "Forward Deployed Engineer" mental model well.

> [!TIP]
> **Observation:** Validation is currently the "last" check.
> **Risk:** If the Planning layer generates an invalid workflow, it propagates to the Execution layer before being caught.
> **Recommendation:** Implement **Local Validation** at every layer boundary. Each layer should validate its *own* output against its contract before passing it to the next stage.

### Layer Patterns
The use of `Classifier`, `Strategy`, `Command`, and `Guard` patterns is excellent. It provides a clear separation of concerns.

---

## 🧩 Schema & Data Flow

### 1. The "Entropy" Problem (State Management)
The spec currently shows data flowing linearly, but it doesn't explicitly define how **Entities** (e.g., Client Name, Meeting Date) extracted in the *Interpretation* layer are passed to the *Execution* layer to populate email content or task descriptions.

*   **Missing Component:** A "Working Memory" or **Context Object**.
*   **Suggested Addition:**
    ```json
    {
      "context": {
        "client_name": "Acme Corp",
        "primary_contact": "John Doe",
        "extracted_dates": ["2026-05-20"]
      }
    }
    ```

### 2. Type Tightness
`step_id` and `type` are defined as `string`.
*   **Recommendation:** Use **Enums** for `type` (e.g., `COMMUNICATION`, `COORDINATION`, `TASK_GENERATION`) to ensure the Execution layer doesn't encounter unknown types.

---

## 🛠️ Operational Gaps

### 1. Persistence & State
The spec treats the system as a "pure function" (Input → Output). In a real-world scenario, OpsAI needs to know if a workflow is "In Progress", "Completed", or "Stalled".
*   **Missing:** Database schema for **Workflow Instances**.
*   **Critical Question:** If the API returns a list of tasks, where are those tasks stored? Who tracks their status?

### 2. Error Handling & Rejection
The current rejection logic is "Invalid JSON -> Retry" and "Missing fields -> Reject".
*   **Nuance needed:** What happens if the AI determines the input is **malicious** or **out of scope** (e.g., "Tell me a joke")?
*   **Recommendation:** Add an `OUT_OF_SCOPE` intent and a dedicated failure response schema.

---

## 🏃 Sprint Plan Validation

### Sprint 1 & 2 Feedback
Sprint 1 combines Interpretation and Planning.
*   **Risk:** These are the two hardest LLM problems.
*   **Suggestion:** Decouple these. Sprint 1 should focus on a **Single-Shot Pipeline** (Interpretation only) to get the "Core Loop" working, then add Planning in Sprint 2.

---

## 💎 Design Aesthetic Polish
The spec references a "calm, AI-first workflow engine."
*   **UX Note:** The spec is currently 100% backend-focused. To deliver on the "Calm UX" promise, the API response needs to support **streaming status updates** (e.g., "Interpreting intent...", "Drafting workflow...") instead of one large POST wait.

---

## ✅ Summary Conclusion
**Score: 8/10**
The spec is technically sound and professionally structured. It avoids the "chatbot trap" and focuses on operational utility. With the addition of a **Context/State Layer** and **Atomic Validation**, it moves from a design document to a production-ready blueprint.
