#!/bin/bash

set -e  # Exit on any error

sleep 1

echo "Updating package lists..."
apt update -y

echo " "

echo " "
echo "Getting basics ..."
echo " "

apt install -y gpg wget curl

echo " "
echo " "
# Clean up unnecessary files
echo "Cleaning up..."
apt clean

echo " "
echo " Installing streamlit ..."
echo " "

# Install Python and pip system-wide
echo "Installing Python and pip..."
apt install -y python3 python3-pip

echo " "

# Install Streamlit, Evtx, and xmltodict system-wide
#echo "Installing Streamlit ..."
#pip install streamlit
if ! pip show streamlit > /dev/null 2>&1; then
    echo "Installing Streamlit ..."
    pip install streamlit
else
    echo "Streamlit is already installed."
fi

echo " "

# Check if /opt/streamlit directory exists, if not create it
if [ ! -d "/opt/syslog-multiplier" ]; then
    echo "Creating directory..."
    mkdir -p /opt/syslog-multiplier
else
    echo "Directory already exists."
fi

# Check if /opt/streamlit/evtx-json directory exists, if not create it
#if [ ! -d "/opt/syslog-mulitplier" ]; then
#    echo "Creating /opt/streamlit/syslog-multiplier directory..."
#    mkdir -p /opt/streamlit/syslog-multiplier
#else
#    echo "/opt/streamlit/syslog-multiplier directory already exists."
#fi
if [ ! -f "/opt/syslog-multiplier/app.py" ]; then
    curl https://raw.githubusercontent.com/chrisjbawden/syslog-multiplier/refs/heads/main/app/app.py -o /opt/syslog-multiplier/app.py
fi

#echo " "
#echo "Installing logstash ..." 
#echo " "

#apt install apt-transport-https -y
#wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | gpg --dearmor -o /usr/share/keyrings/elastic-keyring.gpg
#echo "deb [signed-by=/usr/share/keyrings/elastic-keyring.gpg] https://artifacts.elastic.co/packages/8.x/apt stable main" | tee -a /etc/apt/sources.list.d/elastic-8.x.list
#apt-get update
#apt install logstash -y

if ! dpkg -s logstash >/dev/null 2>&1; then
    echo "Installing Logstash and prerequisites..."
    apt install apt-transport-https -y
    wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | gpg --dearmor -o /usr/share/keyrings/elastic-keyring.gpg
    echo "deb [signed-by=/usr/share/keyrings/elastic-keyring.gpg] https://artifacts.elastic.co/packages/8.x/apt stable main" | tee -a /etc/apt/sources.list.d/elastic-8.x.list
    apt-get update
    apt install logstash -y
else
    echo "Logstash is already installed."
fi



#/usr/share/logstash/bin/logstash-plugin install logstash-output-syslog

if /usr/share/logstash/bin/logstash-plugin list --verbose | grep -q "logstash-output-syslog"; then
    echo "Plugin 'logstash-output-syslog' is already installed."
else
    echo "Installing plugin 'logstash-output-syslog'..."
    /usr/share/logstash/bin/logstash-plugin install logstash-output-syslog
fi



if [ ! -f "/opt/syslog-multiplier/logstash.conf" ]; then
    curl https://raw.githubusercontent.com/chrisjbawden/syslog-multiplier/refs/heads/main/config/logstash.conf -o /opt/syslog-multiplier/logstash.conf
fi

echo "xpack.monitoring.enabled: false" | tee -a /etc/logstash/logstash.yml
echo "config.reload.automatic: true" | tee -a /etc/logstash/logstash.yml
echo "config.reload.interval: 3s" | tee -a /etc/logstash/logstash.yml

echo " "

# Clean up unnecessary files
echo "Cleaning up..."
apt clean

/usr/share/logstash/bin/logstash -f /opt/syslog-multiplier/logstash.conf &

streamlit run /opt/syslog-multiplier/app.py

