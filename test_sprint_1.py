import json
from opsai.core.interpretation import InterpretationService
from dotenv import load_dotenv

# Ensure we're reading the .env correctly
load_dotenv("opsai/.env")

def test_onboarding_intent():
    service = InterpretationService()
    test_input = "We signed Acme Corp. They need onboarding and a kickoff meeting."
    
    print(f"--- Testing Input: {test_input} ---")
    result = service.interpret(test_input)
    print(json.dumps(result, indent=2))
    
    assert result["intent"] == "CLIENT_ONBOARDING"
    assert "Acme" in result["entities"]["organization"]
    print("✅ Sprint 1 - Core Intent Match Success")

if __name__ == "__main__":
    try:
        test_onboarding_intent()
    except Exception as e:
        print(f"❌ Test Failed: {e}")
