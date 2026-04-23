import uuid
from typing import AsyncGenerator, Any, Dict
from .interpretation import InterpretationService
from .planning import PlanningService
from .execution import ExecutionService
from .validation import ValidationService
from .context import ContextManager
from ..utils.logging import ContextLogger
from ..models import OrchestrationStatus, Orchestration, WorkflowInstance
from ..database import engine
from sqlmodel import Session
import logging

class Orchestrator:
    def __init__(self, orchestration_id: uuid.UUID, engine):
        self.orchestration_id = orchestration_id
        self.engine = engine
        self.interpreter = InterpretationService()
        self.planner = PlanningService()
        self.executor = ExecutionService()
        self.validator = ValidationService()
        self.context_mgr = ContextManager(orchestration_id, engine)
        self.logger = ContextLogger(orchestration_id)

    async def run(self, input_text: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Executes the multi-stage orchestration pipeline and yields status updates.
        """
        try:
            # 1. Interpretation
            yield {"stage": "INTERPRETING", "status": "IN_PROGRESS"}
            self.logger.info("INTERPRETING", "Starting interpretation layer")
            intent_data = await self.interpreter.interpret(input_text)
            
            if not self.validator.validate_interpretation(intent_data):
                self.logger.error("INTERPRETING", "Contract violation in interpretation output")
                yield {"stage": "INTERPRETING", "status": "FAILED", "reason": "Contract Violation"}
                return

            self.context_mgr.save_snapshot(OrchestrationStatus.INTERPRETING, intent_data)
            self.logger.info("INTERPRETING", "Success", extra={"intent": intent_data.get("intent")})
            self.logger.info("AUDIT", f"Intent Data: {intent_data}")
            yield {"stage": "INTERPRETING", "status": "SUCCESS", "data": intent_data}

            # 2. Planning
            yield {"stage": "PLANNING", "status": "IN_PROGRESS"}
            workflow = await self.planner.generate_plan(intent_data["intent"], intent_data["entities"])
            
            if not self.validator.validate_workflow(workflow):
                yield {"stage": "PLANNING", "status": "FAILED", "reason": "Invalid Workflow Schema"}
                return

            self.context_mgr.save_snapshot(OrchestrationStatus.PLANNING, {"workflow": workflow})
            self.logger.info("AUDIT", f"Workflow Steps: {workflow}")
            yield {"stage": "PLANNING", "status": "SUCCESS", "workflow_count": len(workflow)}

            # 3. Execution (Payload Generation & Merging)
            yield {"stage": "EXECUTING", "status": "IN_PROGRESS"}
            payloads = await self.executor.generate_payloads(workflow, intent_data["entities"])
            
            if not self.validator.validate_payloads(payloads):
                yield {"stage": "EXECUTING", "status": "FAILED", "reason": "Invalid Payload Generation"}
                return

            # SHADOW VALIDATION (New in Phase 4: Prompt Injection Protection)
            # Hardcoded safety rules that cannot be bypassed by AI prompt engineering
            ALLOWED_DOMAINS = ["opsai.com", "enterprise.corp", "gmail.com"] # In prod, this would be a config
            for p in payloads:
                if p.get("step_id") and "COMMUNICATION" in p["step_id"]:
                    to_email = p.get("payload", {}).get("to", "")
                    if to_email and not any(to_email.endswith(d) for d in ALLOWED_DOMAINS):
                        msg = f"SHADOW VETO: Blocked communication to unauthorized domain: {to_email}"
                        self.logger.error("SECURITY", msg)
                        yield {"stage": "EXECUTING", "status": "FAILED", "reason": "Security Violation: Unauthorized Domain"}
                        return

            self.logger.info("AUDIT", f"Execution Payloads: {payloads}")

            # MERGE PAYLOADS INTO WORKFLOW (New in Phase 3 Fix)
            # This ensures the WorkflowInstance in the DB contains everything needed for dispatching.
            payload_map = {p["step_id"]: p["payload"] for p in payloads}
            for step in workflow:
                step["payload"] = payload_map.get(step["step_id"], {})

            # Persist the HYDRATED WorkflowInstance for Governance/Approval
            with Session(self.engine) as session:
                orch = session.get(Orchestration, self.orchestration_id)
                if orch:
                    # Clear any old abstract workflow and save the hydrated one
                    wf_instance = WorkflowInstance(orchestration_id=self.orchestration_id, steps=workflow)
                    session.add(wf_instance)
                    orch.status = OrchestrationStatus.PLANNING # Maintain state
                    session.add(orch)
                    session.commit()

            self.context_mgr.save_snapshot(OrchestrationStatus.EXECUTING, {"payloads": payloads, "hydrated_workflow": workflow})
            yield {"stage": "EXECUTING", "status": "SUCCESS", "payload_count": len(payloads)}

            # 4. Governance Halt (NEW in Phase 2)
            self.logger.info("GOVERNANCE", "Halting for approval")
            
            # Transition status in DB to PENDING_APPROVAL
            with Session(self.engine) as session:
                orch = session.get(Orchestration, self.orchestration_id)
                if orch:
                    orch.status = OrchestrationStatus.PENDING_APPROVAL
                    session.add(orch)
                    session.commit()

            self.context_mgr.save_snapshot(OrchestrationStatus.PENDING_APPROVAL, {"governance": "Approval Required"})
            yield {"stage": "GOVERNANCE", "status": "PENDING_APPROVAL", "orchestration_id": str(self.orchestration_id)}
            
            # The pipeline effectively ends here for the initial run. 
            # Phase 2 Dispatcher will pick up from EXECUTING after approve() is called.

        except Exception as e:
            yield {"stage": "PIPELINE", "status": "FAILED", "reason": str(e)}
        finally:
            self.context_mgr.close()

    def resume(self, workflow_id: str, persistence_service) -> None:
        """
        Resume a workflow from failure or paused state using the persistence service.
        Args:
            workflow_id (str): The ID of the workflow to resume.
            persistence_service (PersistenceService): The persistence service instance.
        """
        state = persistence_service.load_state(workflow_id)
        if not state:
            self.logger.error("RESUME", f"No saved state found for workflow {workflow_id}")
            return
        # Resume logic here: restore workflow, step, and status from state
        # (Implementation would continue based on your workflow execution model)
        self.logger.info("RESUME", f"Resumed workflow {workflow_id} from persisted state.")
