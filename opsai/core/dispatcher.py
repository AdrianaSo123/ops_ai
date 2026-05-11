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
    orchestration_id: uuid.UUID
    engine: Any
    registry: Any
    context_mgr: ContextManager
    logger: logging.Logger

    def __init__(self, orchestration_id: uuid.UUID, engine: Any, registry: Any) -> None:
        """
        Initialize the Dispatcher.
        Args:
            orchestration_id (uuid.UUID): The orchestration to dispatch.
            engine: SQLModel database engine.
            registry: Driver registry.
        """
        self.orchestration_id = orchestration_id
        self.engine = engine
        self.registry = registry
        self.context_mgr = ContextManager(orchestration_id, engine)
        self.logger = logging.getLogger(f"Dispatcher-{orchestration_id}")

    async def run_pipeline(self) -> None:
        """
        Main execution loop for all steps in the orchestration.
        Returns:
            None
        """
        with Session(self.engine) as session:
            orchestration: Orchestration | None = session.get(Orchestration, self.orchestration_id)
            if not orchestration or not orchestration.workflow:
                self.logger.error(f"Cannot dispatch: Orchestration or Workflow not found.")
                return

            workflow_steps: List[Dict[str, Any]] = orchestration.workflow.steps
            self.logger.info(f"Starting execution for {len(workflow_steps)} steps")

            for step_data in workflow_steps:
                if not await self._execute_and_handle_step(session, orchestration, step_data):
                    self.logger.error(f"Pipeline halted due to step failure.")
                    return

            self._complete_pipeline(session, orchestration)

    async def _execute_and_handle_step(self, session: Session, orchestration: Orchestration, step_data: Dict[str, Any]) -> bool:
        """
        Executes a single step and handles failure.
        Args:
            session (Session): The database session.
            orchestration (Orchestration): The orchestration instance.
            step_data (Dict[str, Any]): The step data.
        Returns:
            bool: True if successful, False otherwise.
        """
        return await self._process_single_step(session, orchestration, step_data)

    def _complete_pipeline(self, session: Session, orchestration: Orchestration) -> None:
        """
        Marks the orchestration as completed and commits the session.
        Args:
            session (Session): The database session.
            orchestration (Orchestration): The orchestration instance.
        """
        orchestration.status = OrchestrationStatus.COMPLETED
        session.add(orchestration)
        session.commit()
        self.logger.info("Orchestration pipeline completed successfully.")

    async def _process_single_step(
        self,
        session: Session,
        orchestration: Orchestration,
        step_data: Dict[str, Any]
    ) -> bool:
        """
        Handles the lifecycle of a single step: status tracking, retries, and snapshots.
        Returns:
            bool: True if successful, False otherwise.
        """
        step_id: Any | None = step_data.get("step_id")

        if self._is_step_already_successful(session, step_id):
            return True

        status_record = self._create_step_status_record(session, step_id)
        self.context_mgr.save_snapshot(
            OrchestrationStatus.EXECUTING,
            {"current_step": step_id, "mode": "PRE_EXECUTION"}
        )

        success, last_error = await self._execute_with_retries(status_record, session, step_data)

        if not success:
            self._handle_step_failure(session, orchestration, step_id)
            return False

        self.context_mgr.save_snapshot(
            OrchestrationStatus.EXECUTING,
            {"current_step": step_id, "mode": "POST_EXECUTION", "result": status_record.result}
        )
        return True

    def _is_step_already_successful(self, session: Session, step_id: Any) -> bool:
        existing_status: StepStatus | None = session.exec(
            select(StepStatus)
            .where(StepStatus.orchestration_id == self.orchestration_id)
            .where(StepStatus.step_id == step_id)
            .where(StepStatus.status == "SUCCESS")
        ).first()
        if existing_status:
            self.logger.info(f"Step {step_id} already SUCCESS. Skipping (Idempotency).")
            return True
        return False

    def _create_step_status_record(self, session: Session, step_id: Any) -> StepStatus:
        status_record = StepStatus(
            orchestration_id=self.orchestration_id,
            step_id=step_id,
            status="PENDING"
        )
        session.add(status_record)
        session.commit()
        session.refresh(status_record)
        return status_record

    async def _execute_with_retries(self, status_record: StepStatus, session: Session, step_data: Dict[str, Any]) -> tuple[bool, Any]:
        success = False
        last_error = None

        @backoff.on_predicate(
            backoff.expo,
            predicate=lambda r: r.get("status") == "FAILED" and r.get("is_recoverable", False),
            max_tries=MAX_RETRIES,
            logger=self.logger
        )
        async def _attempt_dispatch() -> Dict[str, Any]:
            return await self._dispatch_step(step_data)

        try:
            status_record.status = "EXECUTING"
            session.add(status_record)
            session.commit()

            result_data: Dict[str, Any] = await _attempt_dispatch()

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

        return success, last_error

    def _handle_step_failure(self, session: Session, orchestration: Orchestration, step_id: Any) -> None:
        orchestration.status = OrchestrationStatus.FAILED
        session.add(orchestration)
        session.commit()
        self.logger.error(f"Step {step_id} failed after {MAX_RETRIES} attempts.")

    async def _dispatch_step(self, step_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Routes the step to a registered driver.
        Args:
            step_data (Dict[str, Any]): The step data to dispatch.
        Returns:
            Dict[str, Any]: The driver response.
        """
        step_type: Any | None = step_data.get("type")
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
                "is_recoverable": True,  # Assume transient if the driver crashes mysteriously
                "error": str(e)
            }
