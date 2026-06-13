from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...database.session import get_db
from ...database.models import Incident
from ...agents.simulation_agent.agent import simulation_agent
from pydantic import BaseModel

router = APIRouter()

class SimulationRequest(BaseModel):
    action: str
    incident_id: str

class SimulationResponse(BaseModel):
    action: str
    success_probability: float
    downtime_estimate: str
    risk_estimate: str
    recovery_estimate: str

@router.post("", response_model=SimulationResponse)
def simulate_action(payload: SimulationRequest, db: Session = Depends(get_db)):
    """Simulate the SRE impact of running a specific command or mitigation action"""
    incident = db.query(Incident).filter(Incident.id == payload.incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident context not found")
        
    result = simulation_agent.run(payload.action, incident.title)
    
    return {
        "action": payload.action,
        "success_probability": result.get("success_probability", 0.90),
        "downtime_estimate": result.get("downtime_estimate", "0 mins"),
        "risk_estimate": result.get("risk_estimate", "Low risk"),
        "recovery_estimate": result.get("recovery_estimate", "5 mins")
    }
