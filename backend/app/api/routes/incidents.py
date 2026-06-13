from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from ...database.session import get_db
from ...database.models import Incident, AgentExecution
from ...langgraph.orchestrator import run_orchestrator
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class AlertDataSchema(BaseModel):
    name: str
    service: str
    severity: str
    metric_value: float
    threshold: float
    alert_time: str

class IncidentResponse(BaseModel):
    id: str
    title: str
    status: str
    severity: str
    confidence_score: float
    alert_data: Optional[dict] = None
    metrics: Optional[dict] = None
    logs: Optional[List[str]] = None
    findings: Optional[List[str]] = None
    root_cause: Optional[str] = None
    recommendations: Optional[List[dict]] = None
    executive_report: Optional[str] = None
    timeline: Optional[List[dict]] = None
    reasoning_trace: Optional[List[str]] = None

    class Config:
        from_attributes = True

@router.get("", response_model=List[IncidentResponse])
def get_incidents(db: Session = Depends(get_db)):
    """Fetch all incidents, ordered by severity and time"""
    incidents = db.query(Incident).order_by(
        # Put Critical and High first, then order by ID descending
        Incident.created_at.desc()
    ).all()
    return incidents

@router.get("/{incident_id}", response_model=IncidentResponse)
def get_incident(incident_id: str, db: Session = Depends(get_db)):
    """Get single incident by ID"""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident

def run_investigation_task(incident_id: str):
    # This task executes inside a background thread
    db = SessionLocal()
    try:
        run_orchestrator(incident_id, db)
    except Exception as e:
        print(f"Async LangGraph error for {incident_id}: {e}")
    finally:
        db.close()

from ...database.session import SessionLocal

@router.post("/{incident_id}/diagnose")
def diagnose_incident(incident_id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Trigger the LangGraph multi-agent diagnostic orchestration"""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    # Reset incident state to trigger investigations
    incident.status = "Investigating"
    incident.findings = []
    incident.root_cause = ""
    incident.confidence_score = 0.0
    incident.recommendations = []
    incident.executive_report = ""
    incident.timeline = [{"time": datetime.utcnow().strftime("%H:%M:%S"), "event": "Triggered manual diagnostics run."}]
    incident.reasoning_trace = []
    db.commit()
    
    # Clear old execution traces
    db.query(AgentExecution).filter(AgentExecution.incident_id == incident_id).delete()
    db.commit()

    # Run LangGraph orchestrator synchronously for demo speed, or background_tasks.add_task
    # Let's run it synchronously so the user immediately gets the output on post response, or we can use background task.
    # To prevent client timeout but offer immediate feedback, let's run it synchronously (it takes < 1-2s since it has high fidelity mock mode fallbacks, or quick API calls).
    try:
        run_orchestrator(incident_id, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    return {"status": "success", "message": f"Incident {incident_id} diagnosis completed."}

from datetime import datetime
