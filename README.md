


Docker run:
```
docker run -it -d \
  -p 8502:8501 \
  -p 514:514 \
  --name syslog-multiplier \
  ubuntu bash \
  -c "apt update && apt install curl && curl https://raw.githubusercontent.com/chrisjbawden/syslog-multiplier/refs/heads/main/scripts/deploy.sh | bash"
```
