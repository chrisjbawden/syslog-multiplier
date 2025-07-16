FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies and Logstash
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
    wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | gpg --dearmor -o /usr/share/keyrings/elastic-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/elastic-keyring.gpg] https://artifacts.elastic.co/packages/8.x/apt stable main" > /etc/apt/sources.list.d/elastic-8.x.list && \
    apt-get update && \
    apt-get install -y logstash && \
    /usr/share/logstash/bin/logstash-plugin install logstash-output-syslog && \
    pip3 install --break-system-packages --no-cache-dir streamlit evtx xmltodict && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create the persistent data dir and defaults dir
RUN mkdir -p /opt/syslog-multiplier /usr/local/bin/

# Copy default scripts/configs to defaults/
COPY start-logstash.sh /usr/local/bin/start-logstash.sh
COPY boot.sh /usr/local/bin/boot.sh
COPY app.py /usr/local/bin/app.py
COPY logstash.conf /usr/local/bin/logstash.conf

# Make launch script executable
RUN chmod +x /usr/local/bin/boot.sh

# Logstash config tweaks (optional)
RUN echo "xpack.monitoring.enabled: false" >> /etc/logstash/logstash.yml && \
    echo "config.reload.automatic: true" >> /etc/logstash/logstash.yml && \
    echo "config.reload.interval: 3s" >> /etc/logstash/logstash.yml

EXPOSE 8501
EXPOSE 514/tcp
EXPOSE 514/udp

VOLUME ["/opt/syslog-multiplier"]

ENTRYPOINT ["/usr/local/bin/boot.sh"]


