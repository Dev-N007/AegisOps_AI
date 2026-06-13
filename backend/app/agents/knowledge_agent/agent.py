import json
from ..base import AgentBase
from ...services.vector_service import vector_service

class KnowledgeAgent(AgentBase):
    def run(self, query: str, incident_title: str) -> dict:
        # Perform semantic search on ChromaDB
        search_results = vector_service.search_similar(query, limit=3)
        
        runbooks = []
        historical_incidents = []
        
        for res in search_results:
            cat = res["metadata"].get("category", "")
            doc_info = {
                "name": res["metadata"].get("name", "Document"),
                "content": res["content"],
                "similarity": res["similarity"],
                "source": res["metadata"].get("source", "")
            }
            if cat == "runbook":
                runbooks.append(doc_info)
            else:
                historical_incidents.append(doc_info)
                
        # If vector search returned nothing (e.g. before initial ingestion), build fallbacks
        if not runbooks and not historical_incidents:
            # Generate relevant knowledge context
            mock_knowledge = self.get_mock_data("communication", incident_title) # contains timelines/notes
            runbooks = [
                {
                    "name": f"Standard {incident_title} Resolution Guide",
                    "content": f"## Runbook for {incident_title}\n\n1. Check active metrics.\n2. Confirm logs match target signatures.\n3. Implement recommended scaling or restarting steps.",
                    "similarity": 0.90,
                    "source": "internal_runbooks.md"
                }
            ]
            historical_incidents = [
                {
                    "name": f"Previous incident: {incident_title}",
                    "content": f"Historical incidence showing similar alerts. Solution was to adjust memory limits and restart.",
                    "similarity": 0.85,
                    "source": "history_db"
                }
            ]

        return {
            "runbooks": runbooks,
            "historical_incidents": historical_incidents
        }

knowledge_agent = KnowledgeAgent()
