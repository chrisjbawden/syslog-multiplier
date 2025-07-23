#!/bin/bash
set -e

RSYSLOG_CONF="/etc/rsyslog.conf"

echo 'module(load="imklog" mode="off")' > /etc/rsyslog.d/ignore-kernel.conf

RULES_FILE="$(mktemp)"

if [[ -n "$FORWARD_TARGETS" ]]; then
  # Print raw input for debug
  echo "Raw FORWARD_TARGETS: [$FORWARD_TARGETS]"

  # Use IFS=',' and mapfile to handle entries more robustly
  IFS=',' read -ra TARGETS <<< "$FORWARD_TARGETS"
  for target in "${TARGETS[@]}"; do
    # Remove any control characters and whitespace (including CR/LF)
    target=$(echo "$target" | tr -d '\r\n' | xargs)

    # Debug print
    echo "Processing target: [$target]"

    # Split on colon - using shell parameter expansion safer than IFS here
    PROTO="${target%%:*}"
    remainder="${target#*:}"
    IP="${remainder%%:*}"
    PORT="${remainder#*:}"

    # Debug print parsed parts
    echo "Proto: [$PROTO], IP: [$IP], Port: [$PORT]"

    # Validate IP format a bit (basic)
    if [[ ! "$IP" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
      echo "Invalid IP detected: $IP"
      exit 1
    fi

    case "$PROTO" in
      udp)
        echo "*.* @$IP:$PORT" >> "$RULES_FILE"
        ;;
      tcp)
        echo "*.* @@$IP:$PORT" >> "$RULES_FILE"
        ;;
      *)
        echo "Unsupported protocol: $PROTO"
        exit 1
        ;;
    esac
  done
else
  echo "No FORWARD_TARGETS set"
fi

echo -e "\nForwarding rules to be added to rsyslog.conf:"
cat "$RULES_FILE"
echo

sed -e '/{{FORWARD_RULES}}/{
        r '"$RULES_FILE"'
        d
      }' /rsyslog.conf.template > "$RSYSLOG_CONF"

rm -f "$RULES_FILE"

echo -e "\nStarting rsyslog …\n"
exec /usr/sbin/rsyslogd -n
