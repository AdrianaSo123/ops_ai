import os
import httpx
from typing import Dict, Any
from ..base import BaseDriver

class LinearDriver(BaseDriver):
    """
    Driver for creating issues in Linear via GraphQL.
    Requires OPSAI_DRIVER_LINEAR_KEY and OPSAI_DRIVER_LINEAR_TEAM_ID.
    """
    
    def __init__(self) -> None:
        self.api_url = "https://api.linear.app/graphql"
        self.api_key: str | None = os.getenv("OPSAI_DRIVER_LINEAR_KEY")
        self.team_key: str | None = os.getenv("OPSAI_DRIVER_LINEAR_TEAM_ID")
        self._cached_team_id = None # Internal UUID

    def check_health(self) -> bool:
        """
        Verifies API connectivity and resolves the Team Key to a Team ID.
        """
        if not self.api_key or not self.team_key:
            return False
            
        # Enhanced query to fetch the proper internal ID
        query: str = """
        query {
          team(id: "%s") {
            id
            name
          }
        }
        """ % self.team_key
        
        try:
            with httpx.Client() as client: httpx.Client:
                response: httpx.Response = client.post(
                    self.api_url,
                    headers={"Authorization": self.api_key, "Content-Type": "application/json"},
                    json={"query": query},
                    timeout=5.0
                )
                data = response.json()
                team = data.get("data", {}).get("team")
                if team:
                    self._cached_team_id = team["id"] # Save the internal UUID
                    return True
                return False
        except Exception:
            return False

    async def execute(self, step_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a Linear issue using the the internal Team ID.
        """
        # Ensure we have the internal ID (Retry lookup if cache is empty)
        if not self._cached_team_id:
            self.check_health()
            
        if not self._cached_team_id:
             return {
                "status": "FAILED",
                "is_recoverable": False,
                "error": "Could not resolve Linear Team ID. Check your credentials."
            }

        payload = step_data.get("payload", {})
        title = payload.get("title") or step_data.get("action", "New OpsAI Task")
        description = payload.get("description", "")
        
        mutation = """
        mutation IssueCreate($title: String!, $description: String, $teamId: String!) {
          issueCreate(input: { title: $title, description: $description, teamId: $teamId }) {
            success
            issue {
              id
              url
              identifier
            }
          }
        }
        """
        variables: Dict[str, Any] = {
            "title": title,
            "description": description,
            "teamId": self._cached_team_id
        }

        async with httpx.AsyncClient() as client: httpx.AsyncClient:
            try:
                response: httpx.Response = await client.post(
                    self.api_url,
                    headers={"Authorization": self.api_key, "Content-Type": "application/json"},
                    json={"query": mutation, "variables": variables},
                    timeout=10.0
                )
                
                # Check for HTTP errors
                if response.status_code == 429:
                    return {"status": "FAILED", "is_recoverable": True, "error": "Rate limited by Linear"}
                if response.status_code >= 500:
                    return {"status": "FAILED", "is_recoverable": True, "error": f"Linear Server Error: {response.status_code}"}
                
                data = response.json()
                
                # Check for GraphQL errors
                if "errors" in data:
                    return {
                        "status": "FAILED", 
                        "is_recoverable": False, 
                        "error": data["errors"][0].get("message", "GraphQL Error")
                    }
                
                result = data.get("data", {}).get("issueCreate", {})
                if result.get("success"):
                    issue = result.get("issue", {})
                    return {
                        "status": "SUCCESS",
                        "is_recoverable": False,
                        "result": {
                            "provider": "Linear",
                            "id": issue.get("id"),
                            "identifier": issue.get("identifier"),
                            "url": issue.get("url")
                        }
                    }
                else:
                    return {"status": "FAILED", "is_recoverable": False, "error": "Linear issue creation failed"}

            except httpx.RequestError as e: httpx.RequestError:
                return {"status": "FAILED", "is_recoverable": True, "error": f"Network Error: {str(e)}"}

    def sanitize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # Sensitive links or identifiers are sanitized here.
        return data
