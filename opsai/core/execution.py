import os
import json
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

EXECUTION_SYSTEM_PROMPT = """
You are the Execution Layer of OpsAI.
Your job is to convert a list of abstract workflow steps into concrete, executable payloads.

For each step, you must generate a JSON object that is ready for an external system.

TEMPLATES:
- COMMUNICATION (Email): { "to": "email", "subject": "string", "body": "string" }
- COORDINATION (Calendar): { "title": "string", "start": "ISO8601", "duration_min": int }
- TASK_CREATION (Jira/Linear): { "title": "string", "description": "string", "priority": "string" }
- DATA_RETRIEVAL: { "source": "string", "query": "string" }

Hydrate these templates with information from the provided context. 
If an entity is missing (e.g., email address), LEAVE IT EMPTY OR NULL so the driver can handle the error. DO NOT use 'TBD' for email addresses as it invalidates SMTP standards.

EXPECTED JSON OUTPUT:
{
  "payloads": [
    {
      "step_id": "original_step_id",
      "payload": { ...concrete_data... }
    }
  ]
}

Always return valid JSON. Do not include markdown formatting.
"""

class ExecutionService:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in .env")
        self.client = AsyncOpenAI(api_key=self.api_key)

    async def generate_payloads(self, workflow: List[Dict[str, Any]], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Converts workflow steps into concrete payloads using context hydration.
        """
        user_prompt = f"Workflow: {json.dumps(workflow)}\nContext: {json.dumps(context)}"
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": EXECUTION_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={ "type": "json_object" }
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get("payloads", [])
        except Exception as e:
            # Fallback for execution failure
            return []
