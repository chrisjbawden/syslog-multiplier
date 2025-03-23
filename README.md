


Docker run:
```
docker run -it -d \
  -p 8502:8501 \
  -p 514:514 \
  -v multiplier:/opt/syslog-multiplier \
  --name syslog-multiplier \
  chrisjbawden/syslog-multiplier
```

Default code/password: 1234
