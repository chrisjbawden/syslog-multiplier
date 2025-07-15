FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# Install required system packages and dependencies
RUN apt-get update && \
    apt-get install -y \
        bash \
        gpg \
        wget \
        curl \
        python3 \
        python3-pip \
        apt-transport-https \
        lsb-release \
        ca-certificates \
        openjdk-17-jdk && \
    # Add Elastic GPG key and repository for Logstash
    wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | gpg --dearmor -o /usr/share/keyrings/elastic-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/elastic-keyring.gpg] https://artifacts.elastic.co/packages/8.x/apt stable main" > /etc/apt/sources.list.d/elastic-8.x.list && \
    apt-get update && \
    apt-get install -y logstash && \
    # Install Python packages
    pip3 install --no-cache-dir streamlit evtx xmltodict && \
    # Clean up
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create app directory
RUN mkdir -p /opt/syslog-multiplier

# Copy scripts and app files
COPY start-logstash.sh /opt/syslog-multiplier/start-logstash.sh
COPY launch.sh /opt/syslog-multiplier/launch.sh
COPY app.py /opt/syslog-multiplier/app.py
COPY logstash.conf /opt/syslog-multiplier/logstash.conf

# Make scripts executable
RUN chmod +x /opt/syslog-multiplier/start-logstash.sh /opt/syslog-multiplier/launch.sh

# Optionally, add your config tweaks for Logstash here
RUN echo "xpack.monitoring.enabled: false" >> /etc/logstash/logstash.yml && \
    echo "config.reload.automatic: true" >> /etc/logstash/logstash.yml && \
    echo "config.reload.interval: 3s" >> /etc/logstash/logstash.yml

EXPOSE 8501
EXPOSE 514/tcp
EXPOSE 514/udp

# Set the entrypoint to your launch script
ENTRYPOINT ["/opt/syslog-multiplier/launch.sh"]
