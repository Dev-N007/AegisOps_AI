# Runbook: Handling Disk Space Saturation and Storage Full

This guide addresses servers displaying disk space utilization above 95%.

## Symptoms
- System logs report `No space left on device` or `Failed to write log`.
- DB queries failing during temp table creation operations.
- Disk alert triggers critical threshold at 95% full.

## Investigation Steps
1. **Locate Large Directories**:
   Run disk analysis to locate the heavy space consumers:
   ```bash
   df -h
   du -sh /* 2>/dev/null | sort -rh | head -10
   ```
2. **Identify Lock Holders**:
   Ensure large deleted files are not held in memory by running processes (`lsof | grep deleted`).

## Mitigation Actions
1. **Flush Rotated Logs & Caches**:
   Clear old gzipped system logs and package manager cache:
   ```bash
   rm -f /var/log/**/*.gz
   apt-get clean
   docker system prune -af --volumes
   ```
2. **Verify/Expand Volume Storage**:
   If running on cloud instances, expand the persistent volume size using AWS/GCP dynamic resize, then resize the filesystem:
   ```bash
   resize2fs /dev/xvda1
   ```
