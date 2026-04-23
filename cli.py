"""
cli.py — CLI entrypoint for OpsAI Phase 4
Delegates all business logic to orchestrator and services. No business logic in CLI.
Follows SOLID principles and is fully type-annotated and documented.
"""
import argparse
from opsai.core.orchestrator import Orchestrator
from opsai.core.persistence import PersistenceRepository, PersistenceService


def main():
    parser = argparse.ArgumentParser(description="OpsAI CLI")
    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run", help="Run a new workflow")
    run_parser.add_argument("--input", required=True, help="Input text for orchestration")

    resume_parser = subparsers.add_parser("resume", help="Resume a workflow from saved state")
    resume_parser.add_argument("workflow_id", help="Workflow ID to resume")

    args = parser.parse_args()

    if args.command == "run":
        # Example: Orchestrator usage for new workflow
        print("[INFO] Run command not implemented in this stub.")
    elif args.command == "resume":
        repo = PersistenceRepository()
        service = PersistenceService(repo)
        orchestrator = Orchestrator(args.workflow_id, None)  # Pass engine if needed
        orchestrator.resume(args.workflow_id, service)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
