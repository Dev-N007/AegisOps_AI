import json
from ..base import AgentBase

class AlertAgent(AgentBase):
    def run(self, alert_data: dict, metrics: dict) -> dict:
        title = alert_data.get("name", "Unknown Alert")
        
        # Check if we should call the real LLM or use simulation fallback
        try:
            prompt = f"""
            Analyze the following service alert and its associated metrics:
            Alert Data: {json.dumps(alert_data)}
            Current System Metrics: {json.dumps(metrics)}
            
            Perform severity classification and anomaly detection.
            Respond ONLY with a JSON object in this format:
            {{
                "severity": "Critical|High|Medium|Low",
                "confidence": 0.0 to 1.0,
                "likely_issue": "Short summary of likely issue",
                "findings": ["finding 1", "finding 2"]
            }}
            """
            system_instruction = "You are an SRE alert triage assistant. You classify incoming system anomalies."
            result_str = self.call_llm(prompt, system_instruction=system_instruction)
            return json.loads(result_str)
        except Exception:
            # Fallback to high-fidelity mock data based on the alert name
            return self.get_mock_data("alert", title)

alert_agent = AlertAgent()
