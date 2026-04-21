# 📄 OpsAI — Phase 3 System Specification
(Integration Drivers)

---

## 🧠 Overview
Phase 3 transitions OpsAI from a "Closed Simulation" to an "Open Execution" engine. It introduces a modular **Driver Architecture** that allows the system to communicate with real external APIs.

The system transitions from:
“AI simulates actions to mock logs” 
to 
“AI dispatches validated payloads to production APIs”

---

## 🚨 Problem This Phase Solves
Phase 2 limitation:
- actions are only "proof of concept"
- no actual utility in real-world operations
- execution success is hardcoded per step

Phase 3 introduces:
1. **Driver Abstraction**: Decouples the Dispatcher from specific API providers.
2. **Real-World Effects**: Sends real emails, creates real tasks, and posts real messages.
3. **Secret Management**: Securely handles API keys and credentials.

---

## 🎯 System Goals

### Functional
- Instantiate specialized Drivers based on `StepType`.
- **Pre-flight Check**: Validate API keys on system startup (`check_health()`).
- Transform AI-generated JSON into provider-specific API requests (REST/GraphQL).
- **Error Categorization**: Distinguish between `Recoverable` (Retriable) and `Fatal` errors.
- **Sensitive Masking**: Sanitize PII/Secrets before saving to `StepStatus.result`.
- Log real HTTP status codes and API responses.
- Support "Mock Fallback" if API keys are missing.

### Non-Functional
- **Resilience**: Exponential backoff for transient API failures.
- **Security**: Strictly load keys from environment (no hardcoding).
- **Extensibility**: Easy to add a new driver (e.g., swapping SendGrid for Mailgun).

---

## 🧩 System Architecture

### Driver Registry
A central map that associates a `StepType` with a concrete `Driver` class based on configuration.

### Driver Lifecycle
1. **Instantiation**: Load API keys and config.
2. **Health Check**: Verify connectivity and credential validity (`check_health()`).
3. **Translation**: Convert the AI `payload` into `provider_params`.
4. **Execution**: Perform the async HTTP request.
5. **Resolution**: Map the API response to a standard `StepResult` with `is_recoverable` flag.

---

## 📦 Core Interfaces

### Base Driver
```python
class BaseDriver(ABC):
    @abstractmethod
    def check_health(self) -> bool:
        """Validate credentials and connectivity on startup."""
        pass

    @abstractmethod
    async def execute(self, payload: dict) -> dict:
        """
        Execute the action. 
        Returns: {'status': 'SUCCESS'|'FAILED', 'is_recoverable': bool, 'result': dict}
        """
        pass
```

### Supported Drivers (Phase 3 Scope)
- **GmailDriver**: Handles `COMMUNICATION` (email via SMTP/API).
- **LinearDriver**: Handles `TASK_CREATION` (project management).
- **MockDriver**: Fallback for all types when keys are missing.

---

## ⚙️ Driver Logic & Fallback

### Execution Flow (Updated)
```python
# In Dispatcher.py
try:
    driver = registry.get_driver(step.type)
    result = await driver.execute(step.payload)
    
    if result['status'] == 'FAILED' and result['is_recoverable']:
        # Trigger Dispatcher retry loop
except KeyMissingError:
    result = await mock_driver.execute(step.payload) # Fallback for demo
```

### Transformation Layer
Each driver is responsible for mapping AI fields to API fields:
- `EmailDriver`: `payload['to']` -> `SendGrid.personalizations[0].to[0].email`

---

## 🔐 Secret Management
All keys must follow this naming convention:
- `OPSAI_DRIVER_GMAIL_KEY`
- `OPSAI_DRIVER_LINEAR_KEY`

### Snapshot Masking
Drivers must return a `sanitized_result` for database persistence to avoid logging passwords or private tokens.

---

## 🚀 Sprint Plan

### Sprint 1 — Base Architecture
- ABC definition for Drivers.
- Health-check system for credential validation.
- Dynamic Registry implementation.

### Sprint 2 — Communications Driver
- Gmail (SMTP/API) implementation.
- Email sanitization and snapshot masking.

### Sprint 3 — Operations Drivers
- Linear API integration.
- Task status mapping (mapping Linear states to OpsAI states).

### Sprint 4 — Resilience & Polish
- Exponential Backoff implementation in the Dispatcher.
- End-to-end "Live" Demo (Mock vs. Real mode toggling).

---

## 🔥 Final Outcome
After this phase, OpsAI becomes:
**An Operational AI Backbone capable of autonomously managing business processes across real software stacks.**
