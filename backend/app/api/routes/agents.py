from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from ...database.session import get_db
from ...database.models import AgentExecution
from typing import List, Dict, Any

router = APIRouter()

@router.get("")
def get_agents_status(db: Session = Depends(get_db)):
    """Fetch status and execution analytics for all Agents"""
    # Define primary SRE agents
    agent_names = [
        "Alert Analysis",
        "Log Investigation",
        "Root Cause Analysis",
        "Knowledge Retrieval",
        "Resolution Planning",
        "Executive Reporting"
    ]
    
    output = []
    
    # Calculate stats from AgentExecution table
    for name in agent_names:
        stats = db.query(
            func.count(AgentExecution.id).label("total_runs"),
            func.avg(AgentExecution.duration).label("avg_duration")
        ).filter(AgentExecution.agent_name == name).first()
        
        runs = stats.total_runs or 0
        avg_dur = round(stats.avg_duration or 1.2, 2)
        
        # Check if currently executing
        is_active = db.query(AgentExecution).filter(
            AgentExecution.agent_name == name,
            AgentExecution.status == "Running"
        ).count() > 0
        
        # Build status card
        output.append({
            "name": name,
            "status": "idle" if not is_active else "executing",
            "current_task": "Waiting for incident triggers" if not is_active else "Analyzing logs/metrics...",
            "total_executions": runs,
            "avg_response_time": f"{avg_dur}s",
            "confidence": "94%" if "Root" in name or "Alert" in name else "98%",
            "history": get_agent_history(name, db)
        })
        
    return output

def get_agent_history(agent_name: str, db: Session) -> List[Dict[str, Any]]:
    executions = db.query(AgentExecution).filter(
        AgentExecution.agent_name == agent_name
    ).order_by(AgentExecution.start_time.desc()).limit(5).all()
    
    history = []
    for e in executions:
        history.append({
            "incident_id": e.incident_id,
            "status": e.status,
            "duration": f"{round(e.duration or 0, 2)}s",
            "timestamp": e.start_time.strftime("%Y-%m-%d %H:%M:%S")
        })
    return history
