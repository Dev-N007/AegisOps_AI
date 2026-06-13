import json
from ..base import AgentBase

class ResolutionAgent(AgentBase):
    def run(self, root_cause: str, runbooks: list, incident_title: str) -> dict:
        try:
            prompt = f"""
            Based on the determined root cause: "{root_cause}"
            And the retrieved troubleshooting runbooks: {json.dumps(runbooks)}
            For the incident '{incident_title}'
            
            Generate a detailed, prioritized remediation plan.
            Respond ONLY with a JSON object in this format:
            {{
                "plan": [
                    {{"step": 1, "action": "Actionable resolution step", "risk": "Low|Medium|High", "priority": "High|Medium|Low"}}
                ],
                "estimated_time_mins": 10
            }}
            """
            system_instruction = "You are an SRE recovery expert. You write step-by-step instructions to fix software bugs and service downtime."
            result_str = self.call_llm(prompt, system_instruction=system_instruction)
            return json.loads(result_str)
        except Exception:
            return self.get_mock_data("resolution", incident_title)

resolution_agent = ResolutionAgent()
