# Runbook: Mitigating Out-Of-Memory (OOM) Crashes and Memory Leaks

This guide covers resolution steps when a container or virtual machine encounters a memory leak, resulting in OOM kills.

## Symptoms
- Container exits with Exit Code `137` (SIGKILL by OOM Killer).
- System RAM usage displays a linear upward trend over hours or days without stabilization.
- Logs show `java.lang.OutOfMemoryError` or Node.js `JavaScript heap out of memory`.

## Investigation Steps
1. **Analyze Heap Dumps**:
   If enabled, download heap snapshots from S3/Storage and inspect with memory profilers.
2. **Review Metrics**:
   Plot CPU vs memory usage. A steady rising memory line with flat CPU is a clear leak indicator.

## Mitigation Actions
1. **Vertical Scale Memory Limit**:
   Temporarily raise container memory constraints in Kubernetes or server settings to buy debugging time:
   ```yaml
   resources:
     limits:
       memory: "4Gi"
   ```
2. **Revert Recent Deployments**:
   If the memory leak started after a specific git commit, roll back the active service version.
3. **Trigger Garbage Collection / Restart**:
   Restart the pod or VM to clear memory instantly and restore service health.
