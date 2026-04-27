from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class DomainStrategy:
    name: str
    system_prompt: str
    constraints: List[str]
    required_entities: List[str]

# Domain-Specific Strategies
ONBOARDING_STRATEGY = DomainStrategy(
    name="Client Onboarding",
    system_prompt="""You are the Onboarding Strategy Specialist. 
Your goal is to ensure a premium experience for new clients. 
Always include a Welcome Email, a Kickoff Meeting schedule, and a Welcome Gift task.""",
    constraints=["Must mention organization name in every step", "Priority must be HIGH for the first step"],
    required_entities=["organization"]
)

SALES_STRATEGY = DomainStrategy(
    name="Sales Outreach",
    system_prompt="""You are the Sales Growth Professional.
Focus on high-touch personalization. 
Include a research step, a personalized email, and a LinkedIn follow-up task.""",
    constraints=["Never mention pricing in the first email", "Always suggest a 15-minute call"],
    required_entities=["organization", "contact"]
)

IT_STRATEGY = DomainStrategy(
    name="IT Asset Provisioning",
    system_prompt="""You are the IT Operations Manager.
Focus on security and hardware delivery.
Include account creation, hardware ordering (Laptop/Monitor), and a security brief.""",
    constraints=["All hardware must be 'New'", "Priority must be MED"],
    required_entities=["organization", "dates"]
)

class StrategyRegistry:
    def __init__(self) -> None:
        self._strategies: Dict[str, DomainStrategy] = {
            "CLIENT_ONBOARDING": ONBOARDING_STRATEGY,
            "SALES_OUTREACH": SALES_STRATEGY,
            "IT_PROVISIONING": IT_STRATEGY
        }

    def get_strategy(self, intent: str) -> Optional[DomainStrategy]:
        return self._strategies.get(intent)

    def get_all_intents(self) -> List[str]:
        return list(self._strategies.keys())
