from opsai.core.validation import ValidationService

def test_validation_layer():
    v_service = ValidationService()
    
    # 1. Valid Interpretation
    valid_intent = {
        "intent": "CLIENT_ONBOARDING",
        "confidence": 0.95,
        "entities": {"organization": "Acme"}
    }
    assert v_service.validate_interpretation(valid_intent) is True
    
    # 2. Invalid Interpretation (Wrong intent)
    invalid_intent = {
        "intent": "MAKING_COFFEE",
        "confidence": 0.95,
        "entities": {}
    }
    assert v_service.validate_interpretation(invalid_intent) is False
    
    # 3. Valid Workflow
    valid_workflow = [
        {
            "step_id": "step1",
            "type": "COMMUNICATION",
            "action": "Email",
            "owner": "ops",
            "priority": "HIGH"
        }
    ]
    assert v_service.validate_workflow(valid_workflow) is True
    
    # 4. Invalid Workflow (Missing field)
    invalid_workflow = [
        {
            "step_id": "step1",
            "type": "COMMUNICATION",
            "action": "Email"
        }
    ]
    assert v_service.validate_workflow(invalid_workflow) is False
    
    print("✅ Sprint 5 - Validation Guards Success")

if __name__ == "__main__":
    try:
        test_validation_layer()
    except Exception as e:
        print(f"❌ Test Failed: {e}")
        import traceback
        traceback.print_exc()
