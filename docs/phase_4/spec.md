Perfect—this is your **next phase spec (Phase 3)**, focused ONLY on what actually upgrades your system into something that feels **adaptive, stateful, and real-world ready**.

This builds directly on your current system (don’t rewrite—extend).

---

# 📄 OpsAI — Phase 4
 Specification

## (Adaptive Execution + Decision Layer)

---

# 🧠 Overview

Phase 4 evolves OpsAI from a **governed execution system** into an **adaptive workflow system**.

The system will:

* make decisions based on execution results
* dynamically alter workflow paths
* handle failures with structured fallback strategies
* persist state for long-running workflows

---

# 🚨 Problem This Phase Solves

Phase 2 limitation:

* workflows are static
* execution is linear
* failures terminate workflows
* system cannot adapt

---

## Phase 4 introduces:

| Capability         | Outcome              |
| ------------------ | -------------------- |
| Conditional logic  | dynamic workflows    |
| Retry + escalation | resilient execution  |
| Persistent state   | long-lived workflows |
| Feedback loop      | closed-loop system   |

---

# 🎯 System Goals

---

## Functional

* allow branching based on step results
* retry failed steps with limits
* escalate after repeated failure
* persist orchestration state
* resume workflows from failure

---

## Non-Functional

* deterministic branching behavior
* recoverable system state
* minimal complexity increase
* maintain modular architecture

---

# 🧩 Architecture Update

---

## Updated Execution Model

```plaintext
Plan Workflow
   ↓
Execute Step
   ↓
Evaluate Result
   ↓
Branch Decision
   ↓
Next Step / Retry / Escalate
```

---

## New Layer

```plaintext
Execution Layer
   ↓
Decision Layer   ← NEW
```

---

# 🧠 Core Concepts

---

## 1. Conditional Execution

Each step can define:

```python
class Step:
    step_id: str
    type: str
    payload: dict
    on_success: str | None
    on_failure: str | None
```

---

## Example

```plaintext
Step: Send Email
  ↓
SUCCESS → Next Step
FAILURE → Retry or Escalate
```

---

---

## 2. Retry System

---

## StepStatus Update

```python
class StepStatus:
    step_id: str
    status: str
    retries: int
```

---

## Retry Rules

* max retries = 2
* retry only on failure
* retry updates status

---

## Retry Flow

```plaintext
FAILED → RETRY_PENDING → EXECUTING → SUCCESS/FAILED
```

---

---

## 3. Escalation Logic

---

## Trigger

After retries exhausted:

```plaintext
→ trigger escalation step
```

---

## Example Escalation

```python
create_task("Manual intervention required")
```

---

## Escalation Types

* create task
* send alert email
* log high-priority failure

---

---

## 4. Persistent State

---

## Requirement

Store orchestration data beyond runtime.

---

## Minimal Implementation

Use:

* JSON file store OR
* SQLite

---

## Storage Structure

```plaintext
data/
  orchestrations/
    123.json
```

---

## Stored Data

```json
{
  "id": "123",
  "status": "EXECUTING",
  "steps": [...]
}
```

---

---

## 5. Resume Capability

---

## Behavior

System can resume from:

* failed step
* paused state

---

## CLI Command

```bash
python cli.py resume <id>
```

---

---

## 6. Priority-Based Execution

---

## Add Field

```python
priority: str  # HIGH, LOW
```

---

## Behavior

| Priority | Behavior          |
| -------- | ----------------- |
| HIGH     | requires approval |
| LOW      | auto-executes     |

---

---

# ⚙️ Execution Flow (Updated)

---

```plaintext
Create Orchestration
  ↓
Plan Workflow
  ↓
(If HIGH) → Approval Required
  ↓
Execute Step
  ↓
Check Result
  ↓
IF success → next step
IF failure → retry
IF retries exhausted → escalate
  ↓
Continue until complete
```

---

# 🧪 Testing Strategy

---

## Unit Tests

* conditional branching works
* retry count increments
* escalation triggers
* persistence saves correctly

---

## Integration Test

```plaintext
input → execute → fail → retry → fail → escalate → complete
```

---

## Edge Cases

* retry loop limit reached
* missing step mapping
* corrupted state file

---

# 📁 Project Updates

---

## New Files

* `decision_engine.py`
* `persistence.py`

---

## Modified Files

* `dispatcher.py`
* `orchestrator.py`
* `models.py`

---

# 🚀 Sprint Plan

---

## Sprint 1 — Conditional Logic

* add step branching
* update execution flow

---

## Sprint 2 — Retry + Escalation

* implement retry system
* implement escalation

---

## Sprint 3 — Persistence

* save/load orchestration
* resume capability

---

## Sprint 4 — Testing + Polish

* edge cases
* full pipeline test
* CLI updates

---

# 🧠 Demo Scenario (Phase 4)

---

### Input

> “Send onboarding email and follow up”

---

### Execution

1. email fails
2. retry
3. retry fails
4. escalation triggered
5. task created for manual action

---

# 🔥 Final Outcome

After Phase 4, OpsAI becomes:

> A resilient, adaptive AI workflow system that reacts to outcomes and operates under real-world uncertainty

---

# 🧭 Final Note

This phase is the one that makes your system feel:

👉 **real**
👉 **non-linear**
👉 **intelligent beyond prompting**

---

# 🏗️ PHASE 4 IMPLEMENTATION SPEC (Merged)

## OBJECTIVE

Upgrade OpsAI into a **stateful, resilient orchestration engine** capable of:

* Conditional branching (not just linear execution)
* Retry with strategy
* Escalation as first-class behavior
* Persistent state + resumability
* Priority-based execution policies
* Idempotent, safe execution

---

# ARCHITECTURE UPDATE

## Updated Pipeline

User Input
→ Interpreter
→ Planner
→ Validator
→ Approval Layer
→ Executor
→ **Decision Engine (NEW)**
→ Persistence Layer (NEW)
→ Logger

---

# DATA MODEL UPDATES

## Step Model (REQUIRED)

```json
{
  "step_id": 1,
  "action": "send_email",
  "params": {},
  "status": "pending",

  "on_success": "next_step_id",
  "on_failure": "retry",

  "conditions": [
    {
      "if": "retry_count > 2",
      "then": "escalate"
    }
  ],

  "retry_policy": {
    "max_retries": 3,
    "strategy": "exponential_backoff",
    "base_delay_seconds": 2
  },

  "escalation": {
    "actions": [
      {"type": "create_task"},
      {"type": "log_incident"}
    ]
  },

  "priority": "high",

  "execution_policy": {
    "requires_approval": true,
    "timeout_seconds": 300,
    "fallback": "escalate"
  },

  "idempotency_key": "uuid"
}
```

---

## StepStatus Enum

```python
PENDING
RUNNING
SUCCESS
FAILED
RETRYING
ESCALATED
```

---

# MODULES TO IMPLEMENT

---

## 1. decision_engine.py

### Responsibilities:

* Evaluate step outcome
* Determine next step
* Handle conditional logic
* Trigger retry or escalation

### Function Signature:

```python
def evaluate_step(step, result, context) -> str:
    """
    Returns next action:
    - next_step_id
    - 'retry'
    - 'escalate'
    - 'end'
    """
```

### Logic:

* If success → follow `on_success`
* If failure:

  * Check retry policy
  * If retries left → return "retry"
  * Else → return "escalate"
* Evaluate conditions (if present)
* Conditions override default behavior

---

## 2. retry_handler.py

### Responsibilities:

* Execute retry logic
* Apply strategy (exponential backoff)

### Behavior:

* Track retry count per step
* Delay execution based on strategy

```python
delay = base_delay * (2 ** retry_count)
```

---

## 3. escalation_handler.py

### Responsibilities:

* Execute escalation actions

### Supported Actions:

* create_task (use TaskDriver)
* send_alert (mock ok)
* log_incident (store in DB)

---

## 4. persistence.py

### Responsibilities:

* Save workflow state
* Load workflow state
* Enable resume

### Storage:

* SQLite OR JSON file (MVP acceptable)

### Schema:

```json
{
  "workflow_id": "uuid",
  "steps": [...],
  "current_step": 2,
  "status": "running"
}
```

### Functions:

```python
def save_state(workflow): pass
def load_state(workflow_id): pass
```

---

## 5. executor.py (UPDATE)

### Add:

* Idempotency check before execution

### Logic:

```python
if step.idempotency_key in completed_steps:
    skip_execution()
```

* Update status after each step
* Call decision engine after execution

---

## 6. orchestrator.py (UPDATE)

### Responsibilities:

* Manage full workflow lifecycle
* Support resume

### New CLI Commands:

```bash
python main.py run
python main.py resume <workflow_id>
```

---

# EXECUTION FLOW

1. Execute step
2. Save state
3. Pass result → decision_engine
4. Decision engine returns:

   * next step
   * retry
   * escalate
5. Handle accordingly
6. Persist after every transition

---

# PRIORITY HANDLING

## Rules:

* HIGH → requires approval
* MEDIUM → optional approval
* LOW → auto execute

---

# TESTING REQUIREMENTS

## Unit Tests:

* decision_engine branching
* retry logic correctness
* escalation triggers
* persistence save/load

## Integration Test:

* Simulate failure → retry → escalate pipeline

## Edge Cases:

* Retry exceeds max
* Missing next step
* Corrupted state recovery

---

# CONSTRAINTS

* ALL outputs must be structured (no free text)
* NO execution without approval if required
* EVERY step must be persisted
* Drivers must remain modular
* System must be resumable at ANY step

---

# MVP SCOPE

* CLI only (no UI)
* SQLite or JSON persistence
* 2 drivers (email + task)
* Mock integrations acceptable

---

# SUCCESS CRITERIA

System can:

* Execute multi-step workflow
* Handle failure with retry
* Escalate when retries exhausted
* Resume from failure point
* Prevent duplicate execution
* Log full workflow lifecycle

---

# DEMO SCENARIO (REQUIRED)

* Email step fails
* Retries 3 times
* Escalates
* Creates manual intervention task
* Resume workflow after fix


# 📌 Recommendations & Future Considerations

- Ensure escalation actions are extensible for future integrations (e.g., Slack, PagerDuty, SMS, etc.).
- Consider adding API endpoints for orchestration management and monitoring in future phases (not just CLI).
- Document example workflows and expected outputs for easier onboarding and validation.

---

# QA Checklist (Phase 4)

## Functional QA
- [ ] Conditional branching works as specified
- [ ] Retry logic follows policy and increments correctly
- [ ] Escalation triggers after retries exhausted
- [ ] Persistence saves and loads state accurately
- [ ] Resume command restores workflow from failure/paused state
- [ ] Priority handling enforces approval rules
- [ ] Idempotency prevents duplicate execution

## Non-Functional QA
- [ ] All outputs are structured (no free text)
- [ ] System is modular and maintainable
- [ ] State is recoverable after crash/corruption
- [ ] CLI commands are documented and work as expected

## Testing QA


# 🧑‍💻 Implementation Guidance (Professional Standards)

- All interfaces (drivers, handlers, escalation actions) must be explicit and documented with docstrings and type hints.
- Maintain strict separation between orchestration logic and integration logic (drivers, escalation actions, etc.).
- Use dependency injection for drivers and handlers to maximize testability and flexibility.
- Follow SOLID principles (Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion) in all modules.
- Ensure all new code is covered by unit and integration tests as specified.

---

---