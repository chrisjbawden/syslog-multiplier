FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y rsyslog perl && \
    rm -rf /var/lib/apt/lists/*

# Copy your config template and entrypoint script
COPY rsyslog.conf.template /rsyslog.conf.template
COPY entrypoint.sh /entrypoint.sh

# Make entrypoint executable
RUN chmod +x /entrypoint.sh

# Use your entrypoint script as the container entrypoint
ENTRYPOINT ["/entrypoint.sh"]
