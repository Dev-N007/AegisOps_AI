import json
from ..base import AgentBase

class RootCauseAgent(AgentBase):
    def run(self, metrics: dict, log_findings: dict, incident_title: str) -> dict:
        try:
            prompt = f"""
            Analyze system state for incident '{incident_title}':
            Metrics: {json.dumps(metrics)}
            Log Investigation Findings: {json.dumps(log_findings)}
            
            Correlate the log issues with metrics metrics (surges/drops) to pinpoint the exact root cause.
            Respond ONLY with a JSON object in this format:
            {{
                "root_cause": "Detailed explanation of what broke and why, including files/commits/configs if identifiable",
                "confidence_score": 0.0 to 1.0,
                "correlation_summary": "Summary of correlation analysis"
            }}
            """
            system_instruction = "You are an SRE incident post-mortem lead. You correlate multiple streams of data to identify root causes."
            result_str = self.call_llm(prompt, system_instruction=system_instruction)
            return json.loads(result_str)
        except Exception:
            return self.get_mock_data("rca", incident_title)

root_cause_agent = RootCauseAgent()
