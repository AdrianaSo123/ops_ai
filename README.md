# 📄 OpsAI — Governed Enterprise Orchestration

OpsAI is a robust, AI-first workflow engine that transforms ambiguous natural language inputs into planned, approved, and **real-world executed** operations. 

It is designed as a **System of Record** for AI agents, ensuring every reasoning step is tracked, every action is governed by a human, and every integration is resilient.

---

## 🏛️ Architecture & Core Features

OpsAI follows a strict **3-Stage Reasoning Pipeline** with an integrated **Governance Gate**:

1.  **Interpretation**: Classified Intent extraction and Entity identification.
2.  **Planning**: Domain-specific workflow strategy generation (Onboarding, Sales, IT).
3.  **Governance**: Mandatory **PENDING_APPROVAL** state for human-in-the-loop oversight.
4.  **Integrated Execution**: Modular **Driver Architecture** for real-world actions:
    *   📧 **Gmail Driver**: SMTP/SSL with Jinja2 templating support.
    *   🏔️ **Linear Driver**: GraphQL-based issue and task creation.
    *   🤖 **Mock Fallback**: Automatic simulation mode if real drivers are disabled.
5.  **Resilient Dispatcher**: Hardened execution loop with **Exponential Backoff** (via `backoff` library) and granular `StepStatus` tracking.

---

## 🚀 Getting Started

### 1. Installation
```bash
python3 -m pip install -r requirements.txt
```

### 2. Configuration (`.env`)
Copy the `.env.example` and fill in your keys. OpsAI supports a **Mock-to-Live** toggle:
```env
# Enable live drivers by setting these to true
OPSAI_DRIVER_COMMUNICATION_ENABLED=true
OPSAI_DRIVER_TASK_CREATION_ENABLED=true

# Credentials
OPENAI_API_KEY=sk-...
OPSAI_DRIVER_GMAIL_USER=...
OPSAI_DRIVER_GMAIL_PASS=...
OPSAI_DRIVER_LINEAR_KEY=lin_api_...
```

### 3. Running the Server
```bash
python3 -m uvicorn main:app --reload
```
*Note: On startup, OpsAI runs a **🛡️ Startup Health Check** to verify all enabled integrations.*

---

## 📡 Governed API Entry Points

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/orchestrate` | Initialize a new intent interpretation. |
| `POST` | `/api/orchestrate/{id}/approve` | Resume execution and trigger the Dispatcher. |
| `POST` | `/api/orchestrate/{id}/reject` | Terminate the proposed workflow. |
| `GET` | `/api/orchestrate/{id}/stream` | Listen to the SSE Reasoning Pipeline. |

---

## ✅ Testing the System

### Interactive Test Client
Run the interactive client to test end-to-end flows (Interpretation -> Planning -> Execution):
```bash
python3 test_client.py
```

### Automated Test Suite (Pytest)
OpsAI includes a comprehensive suite of unit tests that use **Mocking** to verify logic without calling external APIs:
```bash
python3 -m pytest tests/
```
*Note: This validates the Driver Registry, the Reasoning strategies, and the Mock fallback logic.*

---

---

## 🛡️ Enterprise Strategy Registry
OpsAI supports specialized strategies for different business domains:
- **CLIENT_ONBOARDING**: Welcome flows and gift tracking.
- **SALES_OUTREACH**: High-touch contact management.
- **IT_PROVISIONING**: Asset and security coordination.

---

## 🎓 Core Skills Demonstrated
This project serves as a showcase for high-end **AI Engineering** and **Backend Architecture**:
*   **Architectural Patterns**: Implementation of **Strategy**, **Command**, and **System of Record** patterns for auditable AI execution.
*   **Governance & Safety**: Design of a multi-stage reasoning pipeline with a mandatory human-approval gate.
*   **Resiliency**: Integration of exponential backoff and startup health checks for production-ready API reliability.
*   **SQLModel & FastAPI**: Efficient use of shared-session, asynchronous database interactions with SQLite.
*   **AI Context Hydration**: Advanced techniques for transforming fuzzy user intent into high-fidelity, executable payloads.
