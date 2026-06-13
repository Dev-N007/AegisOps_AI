import json
from ..base import AgentBase

class SimulationAgent(AgentBase):
    def run(self, action: str, incident_title: str) -> dict:
        action_lower = action.lower()
        
        # Check if we should call the real LLM or use simulation fallback
        try:
            prompt = f"""
            Simulate the outcome of performing the following remediation action:
            Action: "{action}"
            Current IncidentContext: "{incident_title}"
            
            Predict success probability, estimated system downtime, risk category, and recovery time.
            Respond ONLY with a JSON object in this format:
            {{
                "success_probability": 0.0 to 1.0,
                "downtime_estimate": "Description of downtime, e.g. '0 mins', '5 mins'",
                "risk_estimate": "Description of risk level, e.g. 'Low risk', 'High risk of socket drops'",
                "recovery_estimate": "Description of recovery time, e.g. '2 mins'"
            }}
            """
            system_instruction = "You are an SRE simulation bot. You predict the impact of server commands and operations."
            result_str = self.call_llm(prompt, system_instruction=system_instruction)
            return json.loads(result_str)
        except Exception:
            # Smart rule-based simulation if LLM fails or is disabled
            if "restart" in action_lower or "reboot" in action_lower:
                if "db" in action_lower or "database" in action_lower or "postgres" in action_lower:
                    return {
                        "success_probability": 0.92,
                        "downtime_estimate": "30-60 seconds (temporary connection drops)",
                        "risk_estimate": "Medium risk, might interrupt active transactions",
                        "recovery_estimate": "2 mins"
                    }
                else:
                    return {
                        "success_probability": 0.95,
                        "downtime_estimate": "0 mins (live pod rolling swap)",
                        "risk_estimate": "Low risk, clean process refresh",
                        "recovery_estimate": "1 min"
                    }
            elif "scale" in action_lower or "add" in action_lower or "increase" in action_lower:
                return {
                    "success_probability": 0.98,
                    "downtime_estimate": "0 mins (warm standby pods)",
                    "risk_estimate": "Low risk, increases cluster capacity",
                    "recovery_estimate": "3 mins"
                }
            elif "revert" in action_lower or "rollback" in action_lower:
                return {
                    "success_probability": 0.90,
                    "downtime_estimate": "1-2 mins (rolling image deployment)",
                    "risk_estimate": "Medium risk, database migrations could desync",
                    "recovery_estimate": "5 mins"
                }
            elif "flush" in action_lower or "clear" in action_lower or "delete" in action_lower:
                if "log" in action_lower or "cache" in action_lower:
                    return {
                        "success_probability": 0.99,
                        "downtime_estimate": "0 mins",
                        "risk_estimate": "Low risk, cleans local disk sectors",
                        "recovery_estimate": "1 min"
                    }
                else:
                    return {
                        "success_probability": 0.50,
                        "downtime_estimate": "Variable",
                        "risk_estimate": "High risk, might destroy active data logs",
                        "recovery_estimate": "10 mins"
                    }
            else:
                # Fallback to default incident metrics
                return self.get_mock_data("simulation", incident_title)

simulation_agent = SimulationAgent()
