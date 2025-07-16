#!/bin/bash
set -e

# Copy missing default files (but never overwrite)
for f in app.py logstash.conf; do
  if [ ! -f /opt/syslog-multiplier/$f ]; then
    cp /usr/local/bin/$f /opt/syslog-multiplier/$f
    echo "Copied missing $f to /opt/syslog-multiplier/"
  fi
done



# Start Logstash in the background
bash /usr/local/bin/start-logstash.sh &

# Start tailing log file (background)
tail -F /opt/syslog-multiplier/logstash.log &

# Start Streamlit app
streamlit run /opt/syslog-multiplier/app.py


