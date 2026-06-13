import json
from ..base import AgentBase

class CommunicationAgent(AgentBase):
    def run(self, incident_title: str, findings: list, root_cause: str, recommendations: list, severity: str) -> dict:
        try:
            prompt = f"""
            Summarize the incident '{incident_title}' (Severity: {severity}):
            Key Findings: {json.dumps(findings)}
            Root Cause: {root_cause}
            Remediation Recommendations: {json.dumps(recommendations)}
            
            Generate a formal SRE post-mortem executive report in Markdown.
            Also generate a timeline of incident events.
            Respond ONLY with a JSON object in this format:
            {{
                "executive_summary": "Short 2-3 sentence overview",
                "executive_report": "# Markdown formatted post-mortem report...",
                "timeline": [
                    {{"time": "HH:MM:SS", "event": "Description of node execution or event status"}}
                ]
            }}
            """
            system_instruction = "You are a lead SRE technical writer. You compile clean incident timelines and professional reports."
            result_str = self.call_llm(prompt, system_instruction=system_instruction)
            return json.loads(result_str)
        except Exception:
            mock = self.get_mock_data("communication", incident_title)
            
            report = f"""# Incident Post-Mortem: {incident_title}
## Severity: {severity}

### 1. Executive Summary
{mock['executive_summary']}

### 2. Root Cause Analysis
{root_cause}

### 3. Immediate Findings & Anomalies
{chr(10).join(f'- {f}' for f in findings)}

### 4. Corrective & Preventative Actions
The following remediation steps were identified by the Resolution Agent:
"""
            for step in recommendations:
                report += f"\n- **Step {step.get('step')}:** {step.get('action')} (Priority: {step.get('priority')}, Risk: {step.get('risk')})"
                
            return {
                "executive_summary": mock["executive_summary"],
                "executive_report": report,
                "timeline": mock["timeline"]
            }

communication_agent = CommunicationAgent()
