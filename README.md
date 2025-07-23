
# Summary

Simple syslog forwarder/multiplier using rsyslog and a automated script to build the config (the environment arguments).

<hr>

# Deployment

Docker run:
```
docker run -d \
  --name syslog-multiplier \
  -p 514:514/udp \
  -p 514:514/tcp \
  -e FORWARD_TARGETS="udp:10.0.0.242:3100,tcp:10.0.0.242:514" \
  syslog-multiplier
```

