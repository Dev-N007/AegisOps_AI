from sqlalchemy import Column, String, Integer, Float, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .session import Base

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    status = Column(String, default="Triggered") # Triggered, Investigating, RCA Found, Knowledge Retrieved, Mitigating, Resolved
    severity = Column(String, default="Medium") # Critical, High, Medium, Low
    confidence_score = Column(Float, default=0.0)
    alert_data = Column(JSON, nullable=True)
    metrics = Column(JSON, nullable=True)
    logs = Column(JSON, nullable=True)
    findings = Column(JSON, nullable=True)
    root_cause = Column(Text, nullable=True)
    recommendations = Column(JSON, nullable=True)
    executive_report = Column(Text, nullable=True)
    timeline = Column(JSON, nullable=True)
    reasoning_trace = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    executions = relationship("AgentExecution", back_populates="incident", cascade="all, delete-orphan")

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    service = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    metric_value = Column(Float, nullable=True)
    threshold = Column(Float, nullable=True)
    alert_time = Column(DateTime, default=datetime.utcnow)
    raw_payload = Column(JSON, nullable=True)

class AgentExecution(Base):
    __tablename__ = "agent_executions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    incident_id = Column(String, ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False)
    agent_name = Column(String, nullable=False) # Alert, Log, RCA, Knowledge, Resolution, Communication, Simulation
    status = Column(String, default="Running") # Running, Completed, Failed
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    duration = Column(Float, nullable=True) # in seconds
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    reasoning_trace = Column(JSON, nullable=True)

    incident = relationship("Incident", back_populates="executions")

class Runbook(Base):
    __tablename__ = "runbooks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    content = Column(Text, nullable=False) # Markdown
    associated_issues = Column(JSON, nullable=True) # List of keywords/alert names
    tags = Column(JSON, nullable=True)

class HistoricalIncident(Base):
    __tablename__ = "historical_incidents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, nullable=False)
    root_cause = Column(Text, nullable=False)
    resolution = Column(Text, nullable=False)
    logs = Column(JSON, nullable=True)
    metrics = Column(JSON, nullable=True)
    tags = Column(JSON, nullable=True)
