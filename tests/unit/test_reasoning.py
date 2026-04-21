import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from opsai.core.interpretation import InterpretationService
from opsai.core.planning import PlanningService

@pytest.mark.asyncio
async def test_interpretation_service_mocked():
    """Verify that InterpretationService handles AI responses correctly using mocks."""
    service = InterpretationService()
    
    # Mock the OpenAI response structure
    mock_choice = MagicMock()
    mock_choice.message.content = '{"intent": "TEST_INTENT", "entities": {"company": "TestCorp"}}'
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    
    with patch.object(service.client.chat.completions, 'create', new_callable=AsyncMock, return_value=mock_response):
        result = await service.interpret("Test input")
        assert result["intent"] == "TEST_INTENT"
        assert result["entities"]["company"] == "TestCorp"

@pytest.mark.asyncio
async def test_planning_service_mocked():
    """Verify that PlanningService creates a workflow from mocked AI output."""
    service = PlanningService()
    
    mock_choice = MagicMock()
    mock_choice.message.content = '{"workflow": [{"step_id": "s1", "type": "COMMUNICATION", "action": "test", "owner": "o1", "priority": "LOW"}]}'
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    
    with patch.object(service.client.chat.completions, 'create', new_callable=AsyncMock, return_value=mock_response):
        workflow = await service.generate_plan("TEST_INTENT", {})
        assert len(workflow) == 1
        assert workflow[0]["step_id"] == "s1"
