import json
from opsai.core.execution import ExecutionService
from dotenv import load_dotenv

load_dotenv("opsai/.env")

def test_execution_layer():
    service = ExecutionService()
    
    workflow = [
        {
            "step_id": "send_welcome_email",
            "type": "COMMUNICATION",
            "action": "Send a welcome email explaining the onboarding process",
            "owner": "ops_lead",
            "priority": "MED"
        }
    ]
    context = {
        "organization": "Acme Corp.",
        "contacts": ["john@acme.com"],
        "dates": ["2026-05-01"],
        "requires_followup": True
    }
    
    print(f"--- Generating Payloads for {len(workflow)} Workflow Steps ---")
    payloads = service.generate_payloads(workflow, context)
    print(json.dumps(payloads, indent=2))
    
    assert len(payloads) > 0
    assert "john@acme.com" in payloads[0]["payload"]["to"] or "Acme" in payloads[0]["payload"]["body"]
    print("✅ Sprint 4 - Execution Layer Success")

if __name__ == "__main__":
    try:
        test_execution_layer()
    except Exception as e:
        print(f"❌ Test Failed: {e}")
