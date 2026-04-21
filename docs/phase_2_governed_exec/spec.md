Got it. Here’s a clean, highly detailed but still time-scoped spec doc for your next phase—rewritten fresh so you can directly turn it into sprints without overbuilding.


⸻


📄 OpsAI — Phase 2 System Specification
(Governed Execution Engine)


⸻


🧠 Overview
OpsAI is a stateful AI workflow orchestration system that converts unstructured inputs into planned, approved, and executed operations.
Phase 2 introduces:
Governance (Human-in-the-Loop approval)
Execution (Dispatcher layer)
State tracking (step-level lifecycle)
The system transitions from:
“AI suggests workflows”
to
“AI plans, pauses, executes, and tracks workflows”


⸻


🚨 Problem This Phase Solves
Phase 1 limitation:
workflows are generated but not acted upon
no control over execution
no visibility into system behavior
Phase 2 introduces:
Capability
Outcome
Approval Gate
prevents blind execution
Dispatcher
simulates real-world actions
Step Tracking
enables observability


⸻


🎯 System Goals


⸻


Functional
Create orchestration from input
Pause workflow before execution
Resume workflow after approval
Execute steps sequentially
Log step-level outcomes


⸻


Non-Functional
deterministic outputs
recoverable system state
observable execution
modular components


⸻


🧩 System Architecture


⸻


Orchestration Lifecycle
CREATED
  ↓
PLANNED
  ↓
PENDING_APPROVAL → REJECTED
  ↓
EXECUTING (w/ Retry Logic)
  ↓
COMPLETED | FAILED | CANCELLED


⸻


Execution Flow
Input
 ↓
Interpretation
 ↓
Workflow Planning
 ↓
Execution Payload Generation
 ↓
PENDING_APPROVAL
 ↓
(Approval Triggered)
 ↓
Dispatcher Execution
 ↓
Step Logging
 ↓
Final State


⸻


📦 Core Data Models


⸻


Orchestration
class Orchestration:
    id: str
    input: str
    intent: str
    workflow: List[Step]
    status: str # CREATED, PLANNED, PENDING_APPROVAL, REJECTED, EXECUTING, COMPLETED, FAILED, CANCELLED
    steps: List[StepStatus]
    created_at: datetime
    updated_at: datetime


⸻


Step
class Step:
    step_id: str
    type: str
    payload: dict


⸻


StepStatus
class StepStatus:
    step_id: str
    status: str  # PENDING, EXECUTING, SUCCESS, FAILED
    result: dict | None
    error: str | None


⸻


🔐 Governance Layer


⸻


Behavior
After workflow + payload generation:
→ orchestration.status = PENDING_APPROVAL
→ system HALTS execution


⸻


Approval/Rejection Endpoints
POST /api/orchestrations/{id}/approve
POST /api/orchestrations/{id}/reject


⸻


Approval Logic
def approve(orchestration_id):
    # 1. Re-validate to ensure data hasn't gone stale during wait
    if not validator.validate(orchestration.workflow):
        orchestration.status = "FAILED"
        return
        
    orchestration.status = "EXECUTING"
    # Take "Pre-Execution" Snapshot
    snapshot_context(orchestration_id, "PRE_EXECUTION")
    dispatcher.run(orchestration)

def reject(orchestration_id):
    orchestration.status = "REJECTED"
    # Log rejection reason in context
    snapshot_context(orchestration_id, "REJECTED")


⸻


Constraints
cannot approve if already executed
cannot approve invalid orchestration
approval triggers execution only once


⸻


⚙️ Dispatcher Layer


⸻


Responsibility
Execute each workflow step and return structured results.


⸻


Execution Loop
MAX_RETRIES = 3

for step in orchestration.workflow:
    # Mandatory Snapshot before each step
    snapshot_context(orchestration_id, f"PRE_STEP_{step.step_id}")
    
    update_status(step, "EXECUTING")

    # Retry Loop
    for attempt in range(MAX_RETRIES):
        try:
            result = dispatch(step)
            update_status(step, "SUCCESS", result)
            # Mandatory Snapshot after successful step
            snapshot_context(orchestration_id, f"POST_STEP_{step.step_id}")
            break # Success, move to next step

        except Exception as e:
            if attempt == MAX_RETRIES - 1:
                update_status(step, "FAILED", error=str(e))
                # Halt execution on critical step failure
                orchestration.status = "FAILED"
                return # Exit dispatcher
            continue # Try again


⸻


Dispatch Routing
def dispatch(step):
    if step.type == "email":
        return send_email_mock(step.payload)

    if step.type == "task":
        return create_task_mock(step.payload)

    if step.type == "meeting":
        return schedule_meeting_mock(step.payload)


⸻


Mock Services


⸻


Email Service
def send_email_mock(payload):
    return {
        "service": "mock_email",
        "status": "sent"
    }


⸻


Task Service
def create_task_mock(payload):
    return {
        "service": "mock_task_manager",
        "status": "created"
    }


⸻


Meeting Service
def schedule_meeting_mock(payload):
    return {
        "service": "mock_calendar",
        "status": "scheduled"
    }


⸻


Failure Handling
if random.random() < 0.1:
    raise Exception("Simulated failure")


⸻


📊 Logging System


⸻


Step Log
{
  "step_id": "send_email",
  "status": "SUCCESS",
  "timestamp": "...",
  "result": {...}
}


⸻


Orchestration Log
{
  "id": "123",
  "status": "COMPLETED",
  "steps": [...]
}


⸻


🧠 Strategy Registry (Minimal)


⸻


Purpose
Map intent → domain-specific workflow logic


⸻


Implementation
STRATEGIES = {
    "client_onboarding": onboarding_strategy,
    "sales_outreach": sales_strategy
}


⸻


Usage
strategy = STRATEGIES[intent]
workflow = strategy.generate()


⸻


Scope
implement max 2 domains
no dynamic loading
no overengineering


⸻


🖥️ Interfaces


⸻


API (Primary)


⸻


Create Orchestration
POST /api/orchestrations


⸻


Approve
POST /api/orchestrations/{id}/approve


⸻


Status
GET /api/orchestrations/{id}


⸻




⸻


CLI (Operator Interface)


⸻


Commands


⸻


Create
python cli.py create "Client onboarding"


⸻


Status
python cli.py status <id>


⸻


Approve
python cli.py approve <id>


⸻


Logs
python cli.py logs <id>


⸻


🧪 Testing Strategy


⸻


Unit Tests
orchestration creation
state transitions
approval logic
dispatcher routing


⸻


Integration Test
input → planned → paused → approved → executed → completed


⸻


Edge Cases
empty input
invalid step type
dispatcher failure


⸻


📁 Project Structure
opsai/
├── core/
│   ├── orchestrator.py
│   ├── dispatcher.py
│   ├── execution.py
│   ├── strategy_registry.py
├── models.py
├── api/
├── cli.py
├── tests/


⸻


🚀 Sprint Plan


⸻


Sprint 1 — Orchestration State
models
lifecycle transitions


⸻


Sprint 2 — Approval System
pause logic
approve endpoint


⸻


Sprint 3 — Dispatcher
execution engine
mock services


⸻


Sprint 4 — Logging + Testing
logs
failure handling
tests


⸻


🧠 Demo Scenario


⸻


Input
“New client onboarding + follow-up”


⸻


System
creates workflow
pauses
waits for approval


⸻


Operator
approve 123


⸻


System
executes steps
logs results
returns final status


⸻


🔥 Final Outcome
After this phase, OpsAI becomes:
A governed, stateful AI orchestration system that executes and tracks workflows
