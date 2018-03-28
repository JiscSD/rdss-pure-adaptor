#!/bin/bash
# Generate cronjob to run Pure adaptor

cat <<EOF > /etc/cron.d/run-pure-adaptor-cron
*/${PURE_POLL_FREQUENCY} * * * * root cd /app && /usr/local/bin/python3 \
-m pure_adaptor.pure_adaptor > /proc/1/fd/1 2>/proc/1/fd/2
EOF

chmod 0644 /etc/cron.d/run-pure-adaptor-cron
cron -f
