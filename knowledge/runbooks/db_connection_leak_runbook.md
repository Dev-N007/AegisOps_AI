# Runbook: Resolving DB Connection Pool Exhaustion

This guide details the steps to identify and resolve Database Connection Pool Exhaustion.

## Symptoms
- System latency spikes above 2000ms.
- Application logs contain:
  - `PostgreSQL: connection limit exceeded`
  - `Timeout waiting for connection from pool`
- Database CPU is normal or low, but active connection count equals the max connection pool size.

## Investigation Steps
1. **Check Active Database Connections**:
   Identify which application nodes are holding onto connections:
   ```sql
   SELECT client_addr, count(*), state 
   FROM pg_stat_activity 
   GROUP BY client_addr, state;
   ```
2. **Review Code for Missing Closes**:
   Look for recent pull requests that forgot to close sessions inside try-finally blocks or failed to return connections to the pool.

## Mitigation Actions
1. **Kill Idle Connections**:
   Force-close idle backend connections:
   ```sql
   SELECT pg_terminate_backend(pid) 
   FROM pg_stat_activity 
   WHERE state = 'idle' AND state_change < now() - interval '5 minutes';
   ```
2. **Increase Connection Pool Limits**:
   Temporarily increase max connections in your API environment configs:
   - Set `DB_MAX_POOL_SIZE` from `20` to `50` (or appropriate limit).
3. **Restart API Service**:
   Restart instances sequentially to release leaked pool references.
