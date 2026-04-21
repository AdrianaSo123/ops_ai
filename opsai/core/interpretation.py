import os
import json
from typing import Dict, Any
from openai import AsyncOpenAI
from dotenv import load_dotenv
from ..models import OrchestrationStatus
from .prompts import SYSTEM_PROMPT, INTERPRETATION_PROMPT

load_dotenv()

class InterpretationService:
    def __init__(self):
        # Defaulting to OpenAI as the primary engine for Intent Classification
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in .env")
        self.client = AsyncOpenAI(api_key=self.api_key)

    async def interpret(self, input_text: str) -> Dict[str, Any]:
        """
        Processes raw input text into a structured intent and entity set.
        """
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o",  # Using a robust model for the reasoning layer
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": INTERPRETATION_PROMPT.format(input_text=input_text)}
                ],
                response_format={ "type": "json_object" }
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
        except Exception as e:
            # Fallback/Error handling for the Interpretation Layer
            # In a production system, we'd log this to our Observability layer (Sprint 7)
            return {
                "intent": "AMBIGUOUS_INPUT",
                "confidence": 0.0,
                "entities": {},
                "error": str(e)
            }
