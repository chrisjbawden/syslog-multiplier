#!/bin/bash
set -e

LOG_FILE="/opt/syslog-multiplier/logstash.log"
mkdir -p "$(dirname "$LOG_FILE")"
touch "$LOG_FILE"

# Start Logstash in the background, logging to a dedicated file
/usr/share/logstash/bin/logstash -f /opt/syslog-multiplier/logstash.conf >> "$LOG_FILE" 2>&1 &
LOGSTASH_PID=$!

# Echo the PID into the log file
echo "[INFO] Logstash started with PID $LOGSTASH_PID" >> "$LOG_FILE"

# Optionally: Wait a moment so the log file gets data
sleep 2

# Done!
exit 0
