# Runbook: Scaling Services During Traffic Surges

This guide details auto-scaling and traffic management procedures during heavy loads.

## Symptoms
- Inbound request volume jumps by over 300%.
- Service CPU utilization stays pinned at 90-100%.
- High request queue times and HTTP 503 Service Unavailable rates.

## Investigation Steps
1. **Determine Traffic Legitimacy**:
   Inspect headers to identify if traffic is a legitimate user surge (flash sale) or a DDoS attack:
   - Check if requests are distributed or originate from similar user-agents/IP ranges.
2. **Review Auto-Scaler Limits**:
   Check if Kubernetes Horizontal Pod Autoscaler (HPA) or AWS Auto-Scaling Groups have hit their max limits.

## Mitigation Actions
1. **Increase Scaling Limits**:
   Quickly bump maximum replicas to allow further scaling:
   ```bash
   kubectl scale deployment api-service --replicas=30
   ```
2. **Apply Cloudflare WAF / Rate Limiting**:
   Enable "I'm Under Attack" mode or WAF rate limit rules to block rogue user agents and scrape bots.
3. **Enable CDN / Static Cache**:
   Increase edge caching durations to lower the backend rendering burden.
