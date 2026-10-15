#!/usr/bin/env bash
# Generate sustained API traffic to drive Prometheus graphs and HPA scale-out.
# Usage: URL=http://clinicflow.local ./scripts/load-test.sh [concurrency] [seconds]
set -euo pipefail
URL="${URL:-http://clinicflow.local}"
CONCURRENCY="${1:-20}"
DURATION="${2:-120}"
end=$((SECONDS + DURATION))

worker() {
  while (( SECONDS < end )); do
    curl -s -o /dev/null "$URL/api/appointments"
    curl -s -o /dev/null "$URL/api/appointments/stats"
    curl -s -o /dev/null "$URL/api/patients?q=a"
  done
}

echo "Hitting $URL with $CONCURRENCY workers for ${DURATION}s"
for _ in $(seq "$CONCURRENCY"); do worker & done
wait
echo "Load test finished"
