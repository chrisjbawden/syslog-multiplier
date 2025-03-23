# Use the official Ubuntu base image
FROM ubuntu:20.04

# Avoid interactive dialogue during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Update package lists and install bash
RUN apt-get update && apt-get install -y bash

# Copy your bash script into the container (upload launch.sh via Portainer)
COPY launch.sh /usr/local/bin/launch.sh

# Grant execute permission to the script
RUN chmod +x /usr/local/bin/launch.sh

# Expose port 8501 for external access
EXPOSE 8501

# Set the entrypoint to execute the bash script on container startup
ENTRYPOINT ["/usr/local/bin/launch.sh"]
