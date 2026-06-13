import time
from typing import TypedDict, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from langgraph.graph import StateGraph, END

# Import agent instances
from ..agents.alert_agent.agent import alert_agent
from ..agents.log_agent.agent import log_agent
from ..agents.root_cause_agent.agent import root_cause_agent
from ..agents.knowledge_agent.agent import knowledge_agent
from ..agents.resolution_agent.agent import resolution_agent
from ..agents.communication_agent.agent import communication_agent
from ..database.models import Incident, AgentExecution
from ..database.session import SessionLocal

# 1. State Definition
class IncidentState(TypedDict):
    incident_id: str
    alert_data: dict
    metrics: dict
    logs: list
    severity: str
    findings: list
    root_cause: str
    historical_incidents: list
    runbooks: list
    recommendations: list
    executive_report: str
    confidence_score: float
    timeline: list
    reasoning_trace: list

# DB logging helpers to track executions live
def _log_execution_start(db: Session, incident_id: str, agent_name: str) -> int:
    exec_record = AgentExecution(
        incident_id=incident_id,
        agent_name=agent_name,
        status="Running",
        start_time=datetime.utcnow()
    )
    db.add(exec_record)
    db.commit()
    db.refresh(exec_record)
    return exec_record.id

def _log_execution_end(db: Session, exec_id: int, status: str, output_data: dict, trace: list):
    exec_record = db.query(AgentExecution).filter(AgentExecution.id == exec_id).first()
    if exec_record:
        exec_record.status = status
        exec_record.end_time = datetime.utcnow()
        duration = (exec_record.end_time - exec_record.start_time).total_seconds()
        exec_record.duration = duration
        exec_record.output_data = output_data
        exec_record.reasoning_trace = trace
        db.commit()

# 2. Node Functions
def alert_analysis_node(state: IncidentState) -> Dict[str, Any]:
    print("[Orchestrator] Alert Analysis Node starting...")
    db = SessionLocal()
    try:
        exec_id = _log_execution_start(db, state["incident_id"], "Alert Analysis")
        
        start_time = time.time()
        result = alert_agent.run(state["alert_data"], state["metrics"])
        duration = time.time() - start_time
        
        trace = [
            f"Parsed alert: {state['alert_data'].get('name')}.",
            f"Evaluated latency ({state['metrics'].get('latency')}ms) and CPU ({state['metrics'].get('cpu')}%).",
            f"Assigned severity: {result.get('severity')} with confidence {result.get('confidence')}."
        ]
        
        # Update Incident State in DB
        incident = db.query(Incident).filter(Incident.id == state["incident_id"]).first()
        if incident:
            incident.status = "Investigating"
            incident.severity = result.get("severity", "Medium")
            db.commit()

        _log_execution_end(db, exec_id, "Completed", result, trace)
        
        return {
            "severity": result.get("severity", "Medium"),
            "confidence_score": result.get("confidence", 0.5),
            "findings": state["findings"] + result.get("findings", []),
            "reasoning_trace": state["reasoning_trace"] + trace
        }
    finally:
        db.close()

def log_investigation_node(state: IncidentState) -> Dict[str, Any]:
    print("[Orchestrator] Log Investigation Node starting...")
    db = SessionLocal()
    try:
        exec_id = _log_execution_start(db, state["incident_id"], "Log Investigation")
        
        start_time = time.time()
        result = log_agent.run(state["logs"], state["alert_data"].get("name", "Unknown"))
        duration = time.time() - start_time
        
        trace = [
            f"Analyzed {len(state['logs'])} log lines.",
            f"Discovered log patterns: {result.get('patterns')}.",
            f"Clustered errors: {', '.join(result.get('clusters', []))}."
        ]
        
        findings_addon = [f"Log Anomaly: {a['message']}" for a in result.get("anomalies", [])]
        
        _log_execution_end(db, exec_id, "Completed", result, trace)
        
        return {
            "findings": state["findings"] + findings_addon,
            "reasoning_trace": state["reasoning_trace"] + trace
        }
    finally:
        db.close()

def root_cause_node(state: IncidentState) -> Dict[str, Any]:
    print("[Orchestrator] Root Cause Agent Node starting...")
    db = SessionLocal()
    try:
        exec_id = _log_execution_start(db, state["incident_id"], "Root Cause Analysis")
        
        start_time = time.time()
        log_findings = {"findings": state["findings"]}
        result = root_cause_agent.run(state["metrics"], log_findings, state["alert_data"].get("name", "Unknown"))
        duration = time.time() - start_time
        
        trace = [
            f"Correlated metric surges with log error patterns.",
            f"Determined root cause: {result.get('root_cause')}.",
            f"Calculated correlation confidence at {result.get('confidence_score')}."
        ]
        
        # Update Incident State in DB
        incident = db.query(Incident).filter(Incident.id == state["incident_id"]).first()
        if incident:
            incident.status = "RCA Found"
            incident.root_cause = result.get("root_cause")
            incident.confidence_score = result.get("confidence_score", 0.8)
            db.commit()

        _log_execution_end(db, exec_id, "Completed", result, trace)
        
        return {
            "root_cause": result.get("root_cause", ""),
            "confidence_score": result.get("confidence_score", 0.8),
            "reasoning_trace": state["reasoning_trace"] + trace
        }
    finally:
        db.close()

def knowledge_retrieval_node(state: IncidentState) -> Dict[str, Any]:
    print("[Orchestrator] Knowledge Retrieval Agent Node starting...")
    db = SessionLocal()
    try:
        exec_id = _log_execution_start(db, state["incident_id"], "Knowledge Retrieval")
        
        start_time = time.time()
        result = knowledge_agent.run(
            query=f"{state['alert_data'].get('name')} {state['root_cause']}",
            incident_title=state["alert_data"].get("name", "Unknown")
        )
        duration = time.time() - start_time
        
        trace = [
            f"Searched vector DB for troubleshooting guides & runbooks.",
            f"Retrieved {len(result.get('runbooks', []))} relevant runbooks.",
            f"Found {len(result.get('historical_incidents', []))} matching historical post-mortems."
        ]
        
        # Update Incident State in DB
        incident = db.query(Incident).filter(Incident.id == state["incident_id"]).first()
        if incident:
            incident.status = "Knowledge Retrieved"
            db.commit()

        _log_execution_end(db, exec_id, "Completed", result, trace)
        
        return {
            "runbooks": result.get("runbooks", []),
            "historical_incidents": result.get("historical_incidents", []),
            "reasoning_trace": state["reasoning_trace"] + trace
        }
    finally:
        db.close()

def resolution_node(state: IncidentState) -> Dict[str, Any]:
    print("[Orchestrator] Resolution Agent Node starting...")
    db = SessionLocal()
    try:
        exec_id = _log_execution_start(db, state["incident_id"], "Resolution Planning")
        
        start_time = time.time()
        result = resolution_agent.run(
            root_cause=state["root_cause"],
            runbooks=state["runbooks"],
            incident_title=state["alert_data"].get("name", "Unknown")
        )
        duration = time.time() - start_time
        
        trace = [
            f"Evaluated remediation strategies based on active runbooks.",
            f"Formulated {len(result.get('plan', []))} action items.",
            f"Estimated time to resolve: {result.get('estimated_time_mins')} minutes."
        ]
        
        # Update Incident State in DB
        incident = db.query(Incident).filter(Incident.id == state["incident_id"]).first()
        if incident:
            incident.status = "Resolution Generated"
            db.commit()

        _log_execution_end(db, exec_id, "Completed", result, trace)
        
        return {
            "recommendations": result.get("plan", []),
            "reasoning_trace": state["reasoning_trace"] + trace
        }
    finally:
        db.close()

def communication_node(state: IncidentState) -> Dict[str, Any]:
    print("[Orchestrator] Communication Agent Node starting...")
    db = SessionLocal()
    try:
        exec_id = _log_execution_start(db, state["incident_id"], "Executive Reporting")
        
        start_time = time.time()
        result = communication_agent.run(
            incident_title=state["alert_data"].get("name", "Unknown"),
            findings=state["findings"],
            root_cause=state["root_cause"],
            recommendations=state["recommendations"],
            severity=state["severity"]
        )
        duration = time.time() - start_time
        
        trace = [
            f"Generated post-mortem executive overview.",
            f"Compiled chronological incident timeline events.",
            f"Structured final markdown incident report."
        ]
        
        # Update Incident State in DB
        incident = db.query(Incident).filter(Incident.id == state["incident_id"]).first()
        if incident:
            incident.status = "Mitigating"
            incident.executive_report = result.get("executive_report")
            incident.timeline = result.get("timeline")
            db.commit()

        _log_execution_end(db, exec_id, "Completed", result, trace)
        
        return {
            "executive_report": result.get("executive_report", ""),
            "timeline": result.get("timeline", []),
            "reasoning_trace": state["reasoning_trace"] + trace
        }
    finally:
        db.close()

# 3. LangGraph workflow construction
workflow = StateGraph(IncidentState)

# Add nodes
workflow.add_node("alert_analysis", alert_analysis_node)
workflow.add_node("log_investigation", log_investigation_node)
workflow.add_node("root_cause", root_cause_node)
workflow.add_node("knowledge_retrieval", knowledge_retrieval_node)
workflow.add_node("resolution", resolution_node)
workflow.add_node("communication", communication_node)

# Set entry point
workflow.set_entry_point("alert_analysis")

# Add edges (strictly orchestrating in sequence)
workflow.add_edge("alert_analysis", "log_investigation")
workflow.add_edge("log_investigation", "root_cause")
workflow.add_edge("root_cause", "knowledge_retrieval")
workflow.add_edge("knowledge_retrieval", "resolution")
workflow.add_edge("resolution", "communication")
workflow.add_edge("communication", END)

# Compile
app = workflow.compile()

# External runner
def run_orchestrator(incident_id: str, db: Session) -> dict:
    """Loads incident from DB, runs LangGraph orchestration, saves result to DB"""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise ValueError(f"Incident with ID {incident_id} not found.")

    # Initialize state from DB models
    initial_state = {
        "incident_id": incident.id,
        "alert_data": incident.alert_data or {},
        "metrics": incident.metrics or {},
        "logs": incident.logs or [],
        "severity": incident.severity or "Medium",
        "findings": incident.findings or [],
        "root_cause": incident.root_cause or "",
        "historical_incidents": [],
        "runbooks": [],
        "recommendations": [],
        "executive_report": "",
        "confidence_score": incident.confidence_score or 0.0,
        "timeline": [],
        "reasoning_trace": []
    }

    print(f"--- Running LangGraph Orchestrator for Incident: {incident_id} ---")
    final_output = app.invoke(initial_state)
    
    # Save final aggregated results back to DB
    incident.findings = final_output.get("findings")
    incident.root_cause = final_output.get("root_cause")
    incident.confidence_score = final_output.get("confidence_score")
    incident.recommendations = final_output.get("recommendations")
    incident.executive_report = final_output.get("executive_report")
    incident.timeline = final_output.get("timeline")
    incident.reasoning_trace = final_output.get("reasoning_trace")
    
    # Keep status updated
    incident.status = "Mitigating"
    db.commit()
    db.refresh(incident)
    
    print(f"--- LangGraph Completed for Incident: {incident_id} ---")
    return final_output

