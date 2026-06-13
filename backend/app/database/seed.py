import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path so we can import app modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.database.session import SessionLocal, engine, Base
from app.database.models import Incident, Alert, Runbook, HistoricalIncident, AgentExecution
from app.rag.ingest import run_ingestion
from app.langgraph.orchestrator import run_orchestrator

def seed_database():
    print("Step 1: Running RAG Ingestion Pipeline...")
    # This imports the runbooks and inserts them into both ChromaDB and relational tables
    run_ingestion()

    db = SessionLocal()
    try:
        print("Step 2: Clearing incidents and executions...")
        db.query(Incident).delete()
        db.query(Alert).delete()
        db.query(AgentExecution).delete()
        db.commit()

        print("Step 3: Seeding 5 core incident templates...")
        
        # 1. Connection Pool Exhaustion (Active, Triggered - ready for user investigation)
        inc_1 = Incident(
            id="INC-2026-001",
            title="Database Connection Pool Exhaustion",
            status="Triggered",
            severity="Critical",
            confidence_score=0.0,
            alert_data={
                "name": "Database Connection Pool Exhaustion",
                "service": "postgres-cluster",
                "severity": "Critical",
                "metric_value": 100.0,
                "threshold": 90.0,
                "alert_time": datetime.utcnow().isoformat()
            },
            metrics={"cpu": 35.2, "memory": 58.1, "latency": 2400.0, "error_rate": 8.4, "connections": 100.0},
            logs=[
                "2026-06-13T23:30:00Z [INFO] router-service inbound HTTP GET /api/v1/orders - latency 2450ms",
                "2026-06-13T23:30:11Z [ERROR] user-profile-service FATAL: remaining connection slots are reserved for non-replication superuser connections",
                "2026-06-13T23:30:15Z [WARNING] user-profile-service HikariPool-1 - Connection is not available, request timed out after 30000ms.",
                "2026-06-13T23:30:20Z [ERROR] order-service django.db.utils.OperationalError: FATAL: remaining connection slots are reserved...",
                "2026-06-13T23:30:22Z [INFO] order-service Retrying connection in 5s..."
            ],
            findings=[],
            timeline=[
                {"time": "23:30:00", "event": "Alert triggered: HTTP 504 rates and API latency spikes detected on gateway."}
            ],
            reasoning_trace=[]
        )

        # 2. Memory Leak (Investigated, resolved)
        inc_2 = Incident(
            id="INC-2026-002",
            title="Memory Leak in Webhooks",
            status="Triggered",
            severity="High",
            alert_data={
                "name": "Memory Leak in Webhooks",
                "service": "payment-webhook",
                "severity": "High",
                "metric_value": 98.2,
                "threshold": 90.0,
                "alert_time": (datetime.utcnow() - timedelta(hours=2)).isoformat()
            },
            metrics={"cpu": 65.5, "memory": 98.2, "latency": 180.0, "error_rate": 2.1},
            logs=[
                "2026-06-13T21:05:00Z [INFO] payment-webhook process active",
                "2026-06-13T21:09:50Z [WARNING] payment-webhook FATAL ERROR: Ineffective mark-compacts near heap limit Allocation failed - JavaScript heap out of memory",
                "2026-06-13T21:10:02Z [FATAL] kernel Killed process 4219 (node) total-vm:4238592kB, anon-rss:4012480kB",
                "2026-06-13T21:10:03Z [INFO] systemd service payment-webhook.service failed with exit code 137. Restarting."
            ],
            findings=[],
            timeline=[],
            reasoning_trace=[]
        )

        # 3. Stripe API Gateway Timeout (Investigated)
        inc_3 = Incident(
            id="INC-2026-003",
            title="Stripe API Gateway Timeout",
            status="Triggered",
            severity="High",
            alert_data={
                "name": "Stripe API Gateway Timeout",
                "service": "checkout-gateway",
                "severity": "High",
                "metric_value": 15200.0,
                "threshold": 5000.0,
                "alert_time": (datetime.utcnow() - timedelta(hours=5)).isoformat()
            },
            metrics={"cpu": 15.0, "memory": 40.5, "latency": 15200.0, "error_rate": 12.5},
            logs=[
                "2026-06-13T18:44:30Z [INFO] checkout-gateway checkout processing initiate",
                "2026-06-13T18:45:01Z [ERROR] payment-service requests.exceptions.ReadTimeout: HTTPSConnectionPool(host='api.stripe.com', port=443): Read timed out. (read timeout=15)",
                "2026-06-13T18:45:10Z [WARNING] router Gateway Timeout encountered on routing proxy. Upstream Stripe API took >15000ms"
            ],
            findings=[],
            timeline=[],
            reasoning_trace=[]
        )

        # 4. Disk Saturation (Investigated)
        inc_4 = Incident(
            id="INC-2026-004",
            title="Disk Saturation on Log Aggregator",
            status="Triggered",
            severity="Critical",
            alert_data={
                "name": "Disk Saturation on Log Aggregator",
                "service": "log-collector",
                "severity": "Critical",
                "metric_value": 99.2,
                "threshold": 95.0,
                "alert_time": (datetime.utcnow() - timedelta(hours=12)).isoformat()
            },
            metrics={"cpu": 22.0, "memory": 45.0, "latency": 95.0, "error_rate": 4.5, "disk_util": 99.2},
            logs=[
                "2026-06-13T11:14:00Z [INFO] log-collector scanning file tables...",
                "2026-06-13T11:15:10Z [ERROR] log-collector OSError: [Errno 28] No space left on device",
                "2026-06-13T11:15:15Z [CRITICAL] log-collector Failed to dump core log file: disk full"
            ],
            findings=[],
            timeline=[],
            reasoning_trace=[]
        )

        # 5. Traffic Spike (Investigated)
        inc_5 = Incident(
            id="INC-2026-005",
            title="Flash Sale Traffic Spike",
            status="Triggered",
            severity="High",
            alert_data={
                "name": "Flash Sale Traffic Spike",
                "service": "edge-proxy",
                "severity": "High",
                "metric_value": 11200.0,
                "threshold": 5000.0,
                "alert_time": (datetime.utcnow() - timedelta(days=1)).isoformat()
            },
            metrics={"cpu": 95.4, "memory": 80.0, "latency": 450.0, "error_rate": 3.2},
            logs=[
                "2026-06-13T21:49:00Z [INFO] edge-proxy connection count 5000 req/s",
                "2026-06-13T21:50:00Z [WARNING] edge-proxy worker connections limit reached (768 worker_connections) while connecting to upstream",
                "2026-06-13T21:50:05Z [INFO] edge-proxy HTTP/2.0 GET /api/v1/deals/flash-sale - 503 Server Too Busy"
            ],
            findings=[],
            timeline=[],
            reasoning_trace=[]
        )

        # 6. Disk Storage Saturated (Active, Triggered - simpler demo scenario)
        inc_6 = Incident(
            id="INC-2026-006",
            title="Disk Storage Saturated (Disk Full)",
            status="Triggered",
            severity="Critical",
            alert_data={
                "name": "Disk Storage Saturated (Disk Full)",
                "service": "api-gateway",
                "severity": "Critical",
                "metric_value": 99.8,
                "threshold": 95.0,
                "alert_time": datetime.utcnow().isoformat()
            },
            metrics={"cpu": 15.0, "memory": 28.0, "latency": 90.0, "error_rate": 5.0, "disk_util": 99.8},
            logs=[
                "2026-06-13T23:50:00Z [INFO] api-gateway proxying inbound traffic normally",
                "2026-06-13T23:55:01Z [ERROR] api-gateway OSError: [Errno 28] No space left on device: '/var/log/nginx/access.log'",
                "2026-06-13T23:55:05Z [CRITICAL] api-gateway write operations blocked, transaction logging failed",
                "2026-06-13T23:55:10Z [ERROR] core-service transaction core dumps fail: disk volume fully saturated"
            ],
            findings=[],
            timeline=[
                {"time": "23:55:01", "event": "Alert triggered: disk saturation threshold reached (99.8%) on volume-01."}
            ],
            reasoning_trace=[]
        )

        # Add all to session
        db.add_all([inc_1, inc_2, inc_3, inc_4, inc_5, inc_6])
        db.commit()

        # Seed Alert history table as well
        for inc in [inc_1, inc_2, inc_3, inc_4, inc_5, inc_6]:
            alt = Alert(
                name=inc.alert_data["name"],
                service=inc.alert_data["service"],
                severity=inc.alert_data["severity"],
                metric_value=inc.alert_data["metric_value"],
                threshold=inc.alert_data["threshold"],
                alert_time=datetime.fromisoformat(inc.alert_data["alert_time"].replace("Z", "+00:00")),
                raw_payload=inc.alert_data
            )
            db.add(alt)
        db.commit()

        print("Step 4: Running LangGraph orchestration on past incidents to generate rich summaries...")
        # Pre-investigate Incidents 2, 3, 4, 5
        run_orchestrator("INC-2026-002", db)
        run_orchestrator("INC-2026-003", db)
        run_orchestrator("INC-2026-004", db)
        run_orchestrator("INC-2026-005", db)

        # Set their status to Resolved/Mitigating to look realistic
        db.query(Incident).filter(Incident.id == "INC-2026-002").update({"status": "Resolved"})
        db.query(Incident).filter(Incident.id == "INC-2026-003").update({"status": "Resolved"})
        db.query(Incident).filter(Incident.id == "INC-2026-004").update({"status": "Resolved"})
        db.query(Incident).filter(Incident.id == "INC-2026-005").update({"status": "Resolved"})
        db.commit()

        print("Database seeding completed successfully.")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
