# Runbook: Resolving API Gateway Timeouts (HTTP 504)

This guide provides steps to diagnose and mitigate Gateway Timeouts from upstream components.

## Symptoms
- Front-facing web portal returns HTTP `504 Gateway Timeout` pages.
- Nginx or Cloudflare error logs indicate `upstream timed out (110: Connection timed out)`.
- Client-side latency reaches the configured load balancer timeout limits.

## Investigation Steps
1. **Identify Upstream Component**:
   Trace which service is timing out (e.g. Payment service, Identity provider, database).
2. **Examine Third-Party Status Pages**:
   Check downstream providers (Stripe, Twilio, AWS) for global outages.

## Mitigation Actions
1. **Enable Circuit Breaking**:
   Trigger circuit breaker to return immediate 503 errors and stop overloading upstream resources:
   - Config: Set `CIRCUIT_BREAKER_ENABLED=true`
2. **Increase Gateway Timeout Limits**:
   If timeouts are due to temporarily heavy operations, raise proxy read timeout settings:
   - `nginx.conf`: `proxy_read_timeout 60s;`
3. **Route Failover**:
   If a regional host is down, route API traffic to an active standby multi-region endpoint.
