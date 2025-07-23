
# Summary

Simple syslog forwarder and duplicator - so you can fork the traffic to additional endpoint. It uses rsyslog with an automated script using the environment arguments provided to build the config.

<hr>

# Deployment

Docker run:
```
docker run -d \
  --name syslog-multiplier \
  -p 514:514/udp \
  -p 514:514/tcp \
  -e FORWARD_TARGETS="udp:10.0.0.242:3100,tcp:10.0.0.242:514" \
  chrisjbawden/syslog-multiplier
```

