#!/bin/bash
set -e

# Start Logstash in the background
bash /opt/syslog-multiplier/start-logstash.sh &

tail -F /opt/syslog-multiplier/logstash.log &

# Start Streamlit app
streamlit run /opt/syslog-multiplier/app.py

