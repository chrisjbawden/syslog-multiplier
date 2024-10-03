#!/bin/bash
sleep 1
apt update

echo " "
echo "Getting basics ..."
echo " "

apt install gpg wget curl

echo " "
echo " Installing streamlit ..."
echo " "

apt install -y python3 python3-pip

pip install streamlit

# Check if /opt/streamlit directory exists, if not create it
if [ ! -d "/opt/streamlit" ]; then
    echo "Creating /opt/streamlit directory..."
    mkdir -p /opt/streamlit
else
    echo "/opt/streamlit directory already exists."
fi

# Check if /opt/streamlit/evtx-json directory exists, if not create it
if [ ! -d "/opt/streamlit/syslog-mulitplier" ]; then
    echo "Creating /opt/streamlit/evtx-json directory..."
    mkdir -p /opt/streamlit/evtx-json
else
    echo "/opt/streamlit/evtx-json directory already exists."
fi

# Check if the app.py file exists in /opt/streamlit/evtx-json, if not download it
if [ ! -f "/opt/streamlit/syslog-mulitplier/app.py" ]; then
    echo "Downloading app.py to /opt/streamlit/evtx-json..."
    curl https://raw.githubusercontent.com/chrisjbawden/syslog-multiplier/refs/heads/main/app/app.py -o /opt/streamlit/syslog-multiplier/app.py
else
    echo "app.py already exists in /opt/streamlit/evtx-json."
fi

echo " "
echo "Installing logstash ..." 
echo " "

apt install apt-transport-https -y
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | gpg --dearmor -o /usr/share/keyrings/elastic-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/elastic-keyring.gpg] https://artifacts.elastic.co/packages/8.x/apt stable main" | tee -a /etc/apt/sources.list.d/elastic-8.x.list
apt-get update && apt-get install logstash -y

curl https://raw.githubusercontent.com/chrisjbawden/syslog-multiplier/refs/heads/main/config/logstash.conf -o /etc/logstash/logstash.conf

echo "xpack.monitoring.enabled: false" | tee -a /etc/logstash/config/logstash.yml
echo "config.reload.automatic: true" | tee -a /etc/logstash/config/logstash.yml
echo "config.reload.interval: 3s" | tee -a /etc/logstash/config/logstash.yml

/usr/share/logstash/bin/logstash -f /etc/logstash/logstash.conf &

streamlit run /opt/streamlit/syslog-multiplier/app.py


