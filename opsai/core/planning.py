import os
import json
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from dotenv import load_dotenv

from opsai.core.strategy_registry import DomainStrategy
from openai.types.chat.chat_completion import ChatCompletion
from .strategy_registry import StrategyRegistry

load_dotenv()

BASE_PLANNING_PROMPT = """
You are the Planning Layer of OpsAI. 
Your job is to translate a structured intent and context into a sequential workflow of steps.

STEP TYPES:
- COMMUNICATION: Sending an email, Slack message, etc.
- COORDINATION: Scheduling a meeting, calendar event.
- TASK_CREATION: Creating a task in a system like Jira/Linear.
- DATA_RETRIEVAL: Fetching additional info from external systems.

EXPECTED JSON OUTPUT:
{
  "workflow": [
    {
      "step_id": "string_id",
      "type": "COMMUNICATION | COORDINATION | TASK_CREATION | DATA_RETRIEVAL",
      "action": "Description of the action",
      "owner": "Who is responsible (e.g., 'ops_lead')",
      "priority": "LOW | MED | HIGH"
    }
  ]
}

Ensure the workflow is minimal, complete, and logically ordered.
Always return valid JSON. Do not include markdown formatting.
"""

class PlanningService:
    def __init__(self) -> None:
        import logging
        logger = logging.getLogger("opsai")
        self.api_key: str | None = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.critical("OPENAI_API_KEY not found in .env")
            raise RuntimeError("OPENAI_API_KEY not found in .env")
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.registry = StrategyRegistry()

    async def generate_plan(self, intent: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generates a multi-step workflow plan based on intent and context.
        """
        # Strategy Lookup
        strategy: DomainStrategy | None = self.registry.get_strategy(intent)
        
        system_prompt: str = BASE_PLANNING_PROMPT
        if strategy:
            system_prompt += f"\n\nDOMAIN SPECIFIC LOGIC ({strategy.name}):\n{strategy.system_prompt}"
            system_prompt += f"\nCONSTRAINTS: {', '.join(strategy.constraints)}"

        user_prompt: str = f"Intent: {intent}\nContext: {json.dumps(context)}"
        
        try:
            response: ChatCompletion = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={ "type": "json_object" }
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get("workflow", [])
        except Exception as e:
            # Fallback strategy
            return [{
                "step_id": "fallback_manual_review",
                "type": "TASK_CREATION",
                "action": f"Manual review required due to planning error: {str(e)}",
                "owner": "admin",
                "priority": "HIGH"
            }]
