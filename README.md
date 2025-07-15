


Docker run:
```
docker run -it -d \
  -p 8502:8501 \
  -p 514:514 \
  -p 514:514/udp \
  --restart unless-stoppped \
  -v multiplier:/opt/syslog-multiplier \
  --name syslog-multiplier \
  chrisjbawden/syslog-multiplier
```

1. Log into the web console http://[ip/url]:8501

      Note: Default code/password: 1234

2. Modify the logstash config and hit save
