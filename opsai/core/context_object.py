"""
Context Object for Orchestration Pipeline
----------------------------------------
This module defines the explicit structure and usage of the Context Object passed between pipeline stages.

The Context Object is a dictionary containing all extracted entities, workflow state, and any additional metadata required for orchestration.

Example Structure:
{
    "intent": "CLIENT_ONBOARDING",
    "entities": {
        "organization": "Acme Corp",
        "contacts": ["john@acme.com"],
        "dates": ["2026-05-01"],
        "requires_followup": true
    },
    "workflow": [...],
    "payloads": [...],
    "governance": "Approval Required",
    "stage": "PLANNING"
}

- The Context Object is snapshotted at every major stage (Interpretation, Planning, Execution, Governance, etc.)
- It is persisted in the `ContextSnapshot` table for full auditability.
- All pipeline components (Orchestrator, Dispatcher, Drivers) should read from and write to this object, not ad-hoc variables.

Usage:
- Use `ContextManager.save_snapshot(stage, context_dict)` to persist the current context.
- Use `ContextManager.get_latest_context()` to retrieve the most recent context for an orchestration.

"""
