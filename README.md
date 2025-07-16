
# Summary

Monolithic Logstash forwarder with Streamlit UI for easy management .

<hr>

# Deployment

Docker run:
```
docker run -it -d \
  -p 8501:8501 \
  -p 514:514 \
  -p 514:514/udp \
  -v [direcotry of your choice]:/opt/syslog-multiplier/ \
  --restart unless-stopped \
  --name syslog-multiplier \
  chrisjbawden/syslog-multiplier
```

# Notes

1. Log into the web console http://[ip/url]:8501

      Note: Default code/password: 1234

2. Modify the logstash config and hit save


---

Directory - /opt/syslog-multiplier/ - stores the streamlit app, logstash config and logstash logs.
