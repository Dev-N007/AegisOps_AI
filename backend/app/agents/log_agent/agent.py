import json
from ..base import AgentBase

class LogAgent(AgentBase):
    def run(self, logs: list, incident_title: str) -> dict:
        try:
            prompt = f"""
            Analyze the following list of application, database, and server logs for an incident titled '{incident_title}':
            Logs: {json.dumps(logs)}
            
            Identify log patterns, cluster errors, and extract anomalous lines.
            Respond ONLY with a JSON object in this format:
            {{
                "anomalies": [
                    {{"timestamp": "...", "level": "...", "message": "..."}}
                ],
                "patterns": "Summary of log patterns seen",
                "clusters": ["cluster 1", "cluster 2"]
            }}
            """
            system_instruction = "You are an SRE log analyzer agent. You parse raw logs to cluster errors and detect system failures."
            result_str = self.call_llm(prompt, system_instruction=system_instruction)
            return json.loads(result_str)
        except Exception:
            return self.get_mock_data("log", incident_title)

log_agent = LogAgent()
