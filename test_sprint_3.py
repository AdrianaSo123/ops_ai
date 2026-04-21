import json
from opsai.core.planning import PlanningService
from dotenv import load_dotenv

load_dotenv("opsai/.env")

def test_planning_layer():
    service = PlanningService()
    
    intent = "CLIENT_ONBOARDING"
    context = {
        "organization": "Acme Corp.",
        "contacts": [],
        "dates": [],
        "requires_followup": True
    }
    
    print(f"--- Generating Plan for Intent: {intent} ---")
    plan = service.generate_plan(intent, context)
    print(json.dumps(plan, indent=2))
    
    assert len(plan) > 0
    assert any(step["type"] in ["COMMUNICATION", "COORDINATION", "TASK_CREATION"] for step in plan)
    print("✅ Sprint 3 - Planning Layer Success")

if __name__ == "__main__":
    try:
        test_planning_layer()
    except Exception as e:
        print(f"❌ Test Failed: {e}")
