import os
import json
import time
from datetime import datetime
import google.generativeai as genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

class AgentBase:
    @staticmethod
    def call_llm(prompt: str, system_instruction: str = "", response_mime_type: str = "application/json") -> str:
        """Helper to call Gemini API if key is present"""
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not configured")
        
        try:
            # Using stable gemini-1.5-flash or gemini-2.5-flash for speed and reliability
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction=system_instruction
            )
            response = model.generate_content(
                prompt,
                generation_config={"response_mime_type": response_mime_type}
            )
            return response.text
        except Exception as e:
            print(f"Gemini API invocation failed: {e}")
            raise e

    @staticmethod
    def get_mock_data(agent_name: str, incident_type: str) -> dict:
        """
        High-fidelity simulated reports, logs, and timelines for the 5 demo incidents.
        This provides fully realized data even when running without API keys.
        """
        incident_type_lower = incident_type.lower()
        
        # 1. CONNECTION POOL EXHAUSTION
        if "pool" in incident_type_lower or "connection" in incident_type_lower:
            if agent_name == "alert":
                return {
                    "severity": "Critical",
                    "confidence": 0.85,
                    "likely_issue": "Database Connection Pool Exhaustion",
                    "findings": [
                        "API Response Latency spiked from 120ms to 2400ms",
                        "Database active connections reached maximum limit (100/100)",
                        "Error rate increased to 8.4% on all /api/v1/orders endpoints"
                    ]
                }
            elif agent_name == "log":
                return {
                    "anomalies": [
                        {"timestamp": "2026-06-13T23:30:11Z", "level": "ERROR", "message": "FATAL: remaining connection slots are reserved for non-replication superuser connections"},
                        {"timestamp": "2026-06-13T23:30:15Z", "level": "WARNING", "message": "HikariPool-1 - Connection is not available, request timed out after 30000ms."},
                        {"timestamp": "2026-06-13T23:30:20Z", "level": "ERROR", "message": "django.db.utils.OperationalError: FATAL: remaining connection slots are reserved..."}
                    ],
                    "patterns": "Repeated pool timeout errors across 4 microservices accessing the main PostgreSQL cluster.",
                    "clusters": ["Connection limit errors (24 occurrences)", "Connection Acquisition timeouts (42 occurrences)"]
                }
            elif agent_name == "rca":
                return {
                    "root_cause": "The main PostgreSQL DB connection pool is exhausted because the newly deployed 'user-profile-service' does not release database connections back to the pool in a timely manner. The leak occurred inside a new middleware session block introduced in commit #d8f1e09.",
                    "confidence_score": 0.94,
                    "correlation_summary": "High correlation (r=0.98) between API response times and database active connections pool occupancy peaking at 100% capacity."
                }
            elif agent_name == "resolution":
                return {
                    "plan": [
                        {"step": 1, "action": "Kill idle database connections to postgres immediately to free up active pools.", "risk": "Low", "priority": "High"},
                        {"step": 2, "action": "Revert commit #d8f1e09 in 'user-profile-service' which introduces the session leak.", "risk": "Medium", "priority": "High"},
                        {"step": 3, "action": "Increase postgres maximum connection limit temporarily from 100 to 200.", "risk": "Low", "priority": "Medium"}
                    ],
                    "estimated_time_mins": 15
                }
            elif agent_name == "communication":
                return {
                    "executive_summary": "At 23:30 UTC, a critical database connection leak disrupted transaction APIs, causing user latencies to climb to 2.4s. An automated rollback and idle-connection termination has been recommended. System is functioning under degraded pool capacity.",
                    "timeline": [
                        {"time": "23:30:00", "event": "Alert triggered: HTTP 504 rates and API latency spikes detected on gateway."},
                        {"time": "23:30:15", "event": "Log Agent parsed db logs and identified HikariPool timeout messages."},
                        {"time": "23:30:35", "event": "RCA Agent correlated the incident with recent deploy commit #d8f1e09."},
                        {"time": "23:30:50", "event": "Knowledge Agent fetched 'DB Connection Pool Exhaustion' runbook."},
                        {"time": "23:31:05", "event": "Resolution Agent constructed remediation plan and submitted for executive approval."}
                    ]
                }
            elif agent_name == "simulation":
                return {
                    "success_probability": 0.95,
                    "downtime_estimate": "0 mins (live reload)",
                    "risk_estimate": "Low risk, frees pool slots instantly",
                    "recovery_estimate": "2 mins"
                }

        # 2. MEMORY LEAK
        elif "memory" in incident_type_lower or "oom" in incident_type_lower:
            if agent_name == "alert":
                return {
                    "severity": "High",
                    "confidence": 0.90,
                    "likely_issue": "Memory Leak / Out-Of-Memory Crash",
                    "findings": [
                        "Memory usage on web-server-pod-2 reached 98% (3.92GB of 4.00GB limit)",
                        "Container restarted dynamically (exit code 137)",
                        "Traffic redirected to web-server-pod-1, causing 20% latency increase"
                    ]
                }
            elif agent_name == "log":
                return {
                    "anomalies": [
                        {"timestamp": "2026-06-13T23:10:02Z", "level": "FATAL", "message": "Killed process 4219 (node) total-vm:4238592kB, anon-rss:4012480kB, file-rss:0kB, shmem-rss:0kB"},
                        {"timestamp": "2026-06-13T23:09:50Z", "level": "WARNING", "message": "FATAL ERROR: Ineffective mark-compacts near heap limit Allocation failed - JavaScript heap out of memory"}
                    ],
                    "patterns": "Linear upward trend of memory usage over 4 hours ending in process SIGKILL.",
                    "clusters": ["OOM Linux Killer events (2 occurrences)", "JavaScript Heap exhaustion (1 occurrence)"]
                }
            elif agent_name == "rca":
                return {
                    "root_cause": "A memory leak was introduced in the payment notification webhook controller where a local array mapping active callback sockets was never cleared, retaining objects in memory indefinitely under high traffic.",
                    "confidence_score": 0.91,
                    "correlation_summary": "System RAM usage showed a steady 15MB/minute growth pattern starting from deployment timestamp 19:00 UTC."
                }
            elif agent_name == "resolution":
                return {
                    "plan": [
                        {"step": 1, "action": "Increase memory limits on kubernetes deployment configurations from 4Gi to 6Gi.", "risk": "Low", "priority": "High"},
                        {"step": 2, "action": "Initiate rolling restart of web-server pods to temporarily reclaim memory.", "risk": "Low", "priority": "High"},
                        {"step": 3, "action": "Apply hotfix to clear callback socket mappings once completed.", "risk": "High", "priority": "Medium"}
                    ],
                    "estimated_time_mins": 10
                }
            elif agent_name == "communication":
                return {
                    "executive_summary": "Web server pods experienced Out-Of-Memory (OOM) crashes due to a slow memory leak in payment webhooks. A rolling restart and capacity scaling have been proposed to prevent repeat crashes while the code is patched.",
                    "timeline": [
                        {"time": "23:09:50", "event": "Node process reports Javascript heap out of memory."},
                        {"time": "23:10:02", "event": "Container exited with code 137. Alert manager routes incident."},
                        {"time": "23:10:30", "event": "Log Agent extracts the kernel OOM killer stack trace."},
                        {"time": "23:11:00", "event": "RCA Agent locates leak inside the payment webhook controller."},
                        {"time": "23:11:15", "event": "Knowledge Agent retrieves OOM Mitigation Runbook."}
                    ]
                }
            elif agent_name == "simulation":
                return {
                    "success_probability": 0.88,
                    "downtime_estimate": "3 mins (rolling update)",
                    "risk_estimate": "Low risk, increases system headroom",
                    "recovery_estimate": "5 mins"
                }

        # 3. API TIMEOUT
        elif "timeout" in incident_type_lower or "gateway" in incident_type_lower or "api" in incident_type_lower:
            if agent_name == "alert":
                return {
                    "severity": "High",
                    "confidence": 0.80,
                    "likely_issue": "Upstream API Gateway Timeout",
                    "findings": [
                        "HTTP 504 Gateway Timeout rates spiked to 12.5% on checkout endpoints",
                        "Downstream stripe-gateway service latency exceeded 15,000ms limit",
                        "Affected checkout flow conversion rate dropped by 65%"
                    ]
                }
            elif agent_name == "log":
                return {
                    "anomalies": [
                        {"timestamp": "2026-06-13T22:45:01Z", "level": "ERROR", "message": "requests.exceptions.ReadTimeout: HTTPSConnectionPool(host='api.stripe.com', port=443): Read timed out. (read timeout=15)"},
                        {"timestamp": "2026-06-13T22:45:10Z", "level": "WARNING", "message": "Gateway Timeout encountered on routing proxy. Upstream Stripe API took >15000ms"}
                    ],
                    "patterns": "Read timeouts specifically occurring during network calls to external Stripe gateway hosts.",
                    "clusters": ["Stripe API Read timeout (31 occurrences)", "Nginx HTTP 504 Upstream failures (28 occurrences)"]
                }
            elif agent_name == "rca":
                return {
                    "root_cause": "The Stripe payment API is experiencing latency spikes globally, causing our internal payment service to consume network sockets waiting for HTTP responses, exceeding the 15-second proxy read timeout limit.",
                    "confidence_score": 0.89,
                    "correlation_summary": "All timed-out requests correspond to transactions requesting Stripe payment tokens. Internal microservices are healthy."
                }
            elif agent_name == "resolution":
                return {
                    "plan": [
                        {"step": 1, "action": "Enable Stripe circuit-breaker parameters to instantly fail-fast and display an alternative error to users.", "risk": "Low", "priority": "High"},
                        {"step": 2, "action": "Route critical transactions to alternative Adyen payment endpoint.", "risk": "Medium", "priority": "High"},
                        {"step": 3, "action": "Notify checkout operators of Stripe partner system outage status.", "risk": "None", "priority": "Low"}
                    ],
                    "estimated_time_mins": 8
                }
            elif agent_name == "communication":
                return {
                    "executive_summary": "External payment integration (Stripe) is experiencing global degradation, generating downstream HTTP 504 timeouts at the gateway. Enabling the API circuit-breaker and toggling checkout fallbacks has been initiated.",
                    "timeline": [
                        {"time": "22:45:01", "event": "Stripe read timeouts hit client thresholds."},
                        {"time": "22:45:15", "event": "Alert manager triggers incident for Stripe API failures."},
                        {"time": "22:45:45", "event": "RCA Agent confirms internal services are normal; external network is the cause."},
                        {"time": "22:46:00", "event": "Knowledge Agent matches API Gateway Timeout Runbook."},
                        {"time": "22:46:20", "event": "Resolution Agent offers routing failover option."}
                    ]
                }
            elif agent_name == "simulation":
                return {
                    "success_probability": 0.90,
                    "downtime_estimate": "0 mins",
                    "risk_estimate": "Medium risk, requires routing validation",
                    "recovery_estimate": "3 mins"
                }

        # 4. DISK SATURATION
        elif "disk" in incident_type_lower or "saturation" in incident_type_lower or "space" in incident_type_lower:
            if agent_name == "alert":
                return {
                    "severity": "Critical",
                    "confidence": 0.95,
                    "likely_issue": "Disk Volume Saturation (Storage Full)",
                    "findings": [
                        "Disk space utilization on log-aggregator-01 reached 99.2% of 500GB volume",
                        "Filesystem write operations blocked",
                        "Local system logging halted"
                    ]
                }
            elif agent_name == "log":
                return {
                    "anomalies": [
                        {"timestamp": "2026-06-13T22:15:10Z", "level": "ERROR", "message": "OSError: [Errno 28] No space left on device"},
                        {"timestamp": "2026-06-13T22:15:15Z", "level": "CRITICAL", "message": "Failed to dump core log file: disk full"}
                    ],
                    "patterns": "Storage writes failing across system processes. Logs cannot append or roll.",
                    "clusters": ["Out of Space disk writes (15 occurrences)", "Core dump writing failures (3 occurrences)"]
                }
            elif agent_name == "rca":
                return {
                    "root_cause": "The `/var/log` directory is saturated with un-rotated debugging logs from a recently configured test log tracer which generated 150GB of raw text in less than 24 hours.",
                    "confidence_score": 0.98,
                    "correlation_summary": "Storage usage jumped from 68% to 99% immediately after the debug trace flag was enabled in environment configurations."
                }
            elif agent_name == "resolution":
                return {
                    "plan": [
                        {"step": 1, "action": "Run system log prune and remove uncompressed rotated files.", "risk": "Low", "priority": "High"},
                        {"step": 2, "action": "Disable debug logging level in configurations to stop excessive log generation.", "risk": "Low", "priority": "High"},
                        {"step": 3, "action": "Trigger EBS volume auto-expand script to add 100GB to the block device.", "risk": "Low", "priority": "Medium"}
                    ],
                    "estimated_time_mins": 5
                }
            elif agent_name == "communication":
                return {
                    "executive_summary": "System block storage hit 99% capacity due to debug log pollution, preventing all application writes. Deleting non-critical historical files and disabling debug traces has been requested.",
                    "timeline": [
                        {"time": "22:15:10", "event": "Disk volume reports disk full state."},
                        {"time": "22:15:30", "event": "Log Agent extracts OSError Errno 28 from trace logs."},
                        {"time": "22:16:00", "event": "RCA Agent maps disk growth with debug logging activation."},
                        {"time": "22:16:30", "event": "Knowledge Agent selects Disk Saturation Runbook."},
                        {"time": "22:17:00", "event": "Resolution Agent triggers automatic volume cleanup steps."}
                    ]
                }
            elif agent_name == "simulation":
                return {
                    "success_probability": 0.99,
                    "downtime_estimate": "0 mins",
                    "risk_estimate": "Low risk, safe log cleanup",
                    "recovery_estimate": "1 min"
                }

        # 5. TRAFFIC SPIKE
        else:
            if agent_name == "alert":
                return {
                    "severity": "High",
                    "confidence": 0.88,
                    "likely_issue": "Unexpected High Traffic Spike",
                    "findings": [
                        "Inbound request volume rose by 410% in 5 minutes (from 2.2k req/sec to 11.2k req/sec)",
                        "CPU utilization on edge-proxy servers reached 95%",
                        "Request dropped rate increased to 3.2%"
                    ]
                }
            elif agent_name == "log":
                return {
                    "anomalies": [
                        {"timestamp": "2026-06-13T21:50:00Z", "level": "WARNING", "message": "worker connections limit reached (768 worker_connections) while connecting to upstream"},
                        {"timestamp": "2026-06-13T21:50:05Z", "level": "INFO", "message": "HTTP/2.0 GET /api/v1/deals/flash-sale - 503 Server Too Busy"}
                    ],
                    "patterns": "Massive volume of requests targeting the flash-sale path. Connection limits saturated.",
                    "clusters": ["Worker connection limits (12 occurrences)", "Flash sale HTTP 503 errors (35 occurrences)"]
                }
            elif agent_name == "rca":
                return {
                    "root_cause": "An unexpected marketing email push triggered a sudden rush of users accessing the '/api/v1/deals/flash-sale' endpoint, exhausting the capacity of our Nginx edge proxy configurations.",
                    "confidence_score": 0.95,
                    "correlation_summary": "Direct correlation between the email newsletter push at 21:45 and edge traffic spikes."
                }
            elif agent_name == "resolution":
                return {
                    "plan": [
                        {"step": 1, "action": "Increase Nginx maximum worker connections dynamically and reload proxy.", "risk": "Low", "priority": "High"},
                        {"step": 2, "action": "Scale microservice instances from 5 replicas to 15.", "risk": "Low", "priority": "High"},
                        {"step": 3, "action": "Apply Cloudflare rate limiting rules on the deals endpoint.", "risk": "Medium", "priority": "Medium"}
                    ],
                    "estimated_time_mins": 12
                }
            elif agent_name == "communication":
                return {
                    "executive_summary": "Edge servers are struggling under a 4x traffic surge targeting /flash-sale. Horizontal scaling and edge connection limit expansions are recommended immediately to recover dropped packets.",
                    "timeline": [
                        {"time": "21:45:00", "event": "Email blast dispatched to subscriber list."},
                        {"time": "21:50:00", "event": "Nginx reports worker connection exhaustion."},
                        {"time": "21:50:20", "event": "Log Agent clusters flash sale GET paths."},
                        {"time": "21:51:00", "event": "RCA Agent correlates email launch with request surges."},
                        {"time": "21:51:30", "event": "Resolution Agent generates traffic scale response."}
                    ]
                }
            elif agent_name == "simulation":
                return {
                    "success_probability": 0.93,
                    "downtime_estimate": "0 mins",
                    "risk_estimate": "Low risk, increases network limits",
                    "recovery_estimate": "4 mins"
                }
