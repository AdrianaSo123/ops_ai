import uuid
import json
import asyncio
import logging
import backoff
from typing import Dict, Any, List
from sqlmodel import Session, select
from ..database import engine
from ..models import Orchestration, OrchestrationStatus, StepStatus
from .context import ContextManager
from .drivers.registry import registry

MAX_RETRIES = 3

class Dispatcher:
    """
    The Dispatcher is the 'heart' of Governed Execution. 
    It executes planned steps, manages retries, and maintains the granular state of the workflow.
    """
    def __init__(self, orchestration_id: uuid.UUID, engine, registry):
        self.orchestration_id = orchestration_id
        self.engine = engine
        self.registry = registry
        self.context_mgr = ContextManager(orchestration_id, engine)
        self.logger = logging.getLogger(f"Dispatcher-{orchestration_id}")

    async def run_pipeline(self):
        """
        Main execution loop for all steps in the orchestration.
        """
        with Session(self.engine) as session:
            # 1. Fetch orchestration with workflow
            orchestration = session.get(Orchestration, self.orchestration_id)
            if not orchestration or not orchestration.workflow:
                self.logger.error(f"Cannot dispatch: Orchestration or Workflow not found.")
                return

            workflow_steps = orchestration.workflow.steps
            self.logger.info(f"Starting execution for {len(workflow_steps)} steps")

            for step_data in workflow_steps:
                success = await self._process_single_step(session, orchestration, step_data)
                
                if not success:
                    self.logger.error(f"Pipeline halted due to step failure.")
                    return # Halt execution

            # E. Pipeline Completion
            orchestration.status = OrchestrationStatus.COMPLETED
            session.add(orchestration)
            session.commit()
            self.logger.info("Orchestration pipeline completed successfully.")

    async def _process_single_step(self, session: Session, orchestration: Orchestration, step_data: Dict[str, Any]) -> bool:
        """
        Handles the lifecycle of a single step: status tracking, retries, and snapshots.
        Returns True if successful, False otherwise.
        """
        step_id = step_data.get("step_id")

        # 0. Idempotency Check: Skip if already successful
        existing_status = session.exec(
            select(StepStatus)
            .where(StepStatus.orchestration_id == self.orchestration_id)
            .where(StepStatus.step_id == step_id)
            .where(StepStatus.status == "SUCCESS")
        ).first()
        if existing_status:
            self.logger.info(f"Step {step_id} already SUCCESS. Skipping (Idempotency).")
            return True

        # A. Create StepStatus record
        status_record = StepStatus(
            orchestration_id=self.orchestration_id,
            step_id=step_id,
            status="PENDING"
        )
        session.add(status_record)
        session.commit()
        session.refresh(status_record)

        # B. Pre-Step Snapshot
        self.context_mgr.save_snapshot(
            OrchestrationStatus.EXECUTING, 
            {"current_step": step_id, "mode": "PRE_EXECUTION"}
        )

        # C. Execution with Backoff Retries
        success = False
        last_error = None

        @backoff.on_predicate(
            backoff.expo, 
            predicate=lambda r: r.get("status") == "FAILED" and r.get("is_recoverable", False),
            max_tries=MAX_RETRIES,
            logger=self.logger
        )
        async def _attempt_dispatch():
            return await self._dispatch_step(step_data)

        try:
            status_record.status = "EXECUTING"
            session.add(status_record)
            session.commit()

            result_data = await _attempt_dispatch()
            
            if result_data["status"] == "SUCCESS":
                status_record.status = "SUCCESS"
                status_record.result = result_data.get("result")
                session.add(status_record)
                session.commit()
                success = True
            else:
                last_error = result_data.get("error", "Fatal driver error")
                status_record.status = "FAILED"
                status_record.error = last_error
                session.add(status_record)
                session.commit()

        except Exception as e:
            last_error = str(e)
            self.logger.error(f"Step {step_id} execution CRASHED: {e}")
            status_record.status = "FAILED"
            status_record.error = last_error
            session.add(status_record)
            session.commit()

        if not success:
            # Update Orchestration status to FAILED
            orchestration.status = OrchestrationStatus.FAILED
            session.add(orchestration)
            session.commit()
            self.logger.error(f"Step {step_id} failed after {MAX_RETRIES} attempts.")
            return False

        # D. Post-Step Snapshot
        self.context_mgr.save_snapshot(
            OrchestrationStatus.EXECUTING, 
            {"current_step": step_id, "mode": "POST_EXECUTION", "result": status_record.result}
        )
        return True

    async def _dispatch_step(self, step_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Routes the step to a registered driver.
        """
        step_type = step_data.get("type")
        driver = self.registry.get_driver(step_type)
        
        try:
            # Execute the driver
            response = await driver.execute(step_data)
            
            # Sanitize the result for the database
            if response.get("result"):
                response["result"] = driver.sanitize(response["result"])
            
            return response
        except Exception as e:
            return {
                "status": "FAILED",
                "is_recoverable": True, # Assume transient if the driver crashes mysteriously
                "error": str(e)
            }
