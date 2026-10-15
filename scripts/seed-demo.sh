#!/usr/bin/env bash
# Book a realistic day of appointments against a running ClinicFlow API.
# Usage: BASE_URL=http://localhost:3000 ./scripts/seed-demo.sh
set -euo pipefail
BASE_URL="${BASE_URL:-http://localhost:3000}"
TODAY="$(date +%F)"
TOMORROW="$(date -d tomorrow +%F 2>/dev/null || date -v+1d +%F)"

post() { curl -sS -o /dev/null -w "%{http_code} $1 $2\n" -X POST "$BASE_URL/api/$1" -H 'Content-Type: application/json' -d "$2"; }

post patients '{"full_name":"Ishaan Gupta","phone":"+91 98860 22114","email":"ishaan@example.com","date_of_birth":"1978-02-09"}'
post patients '{"full_name":"Sara Thomas","phone":"+91 99452 33001","email":"sara@example.com","date_of_birth":"1995-08-30"}'

# doctor_id/patient_id refer to the demo rows created by the 0002 seed migration.
post appointments "{\"doctor_id\":1,\"patient_id\":1,\"scheduled_at\":\"${TODAY}T09:00:00\",\"reason\":\"Fever and sore throat\"}"
post appointments "{\"doctor_id\":2,\"patient_id\":2,\"scheduled_at\":\"${TODAY}T09:30:00\",\"reason\":\"ECG follow-up\"}"
post appointments "{\"doctor_id\":3,\"patient_id\":3,\"scheduled_at\":\"${TODAY}T10:00:00\",\"reason\":\"Vaccination\"}"
post appointments "{\"doctor_id\":1,\"patient_id\":4,\"scheduled_at\":\"${TODAY}T11:30:00\",\"reason\":\"Annual check-up\"}"
post appointments "{\"doctor_id\":4,\"patient_id\":5,\"scheduled_at\":\"${TODAY}T15:00:00\",\"reason\":\"Skin rash\"}"
post appointments "{\"doctor_id\":2,\"patient_id\":1,\"scheduled_at\":\"${TODAY}T16:30:00\",\"reason\":\"Blood pressure review\"}"
post appointments "{\"doctor_id\":1,\"patient_id\":2,\"scheduled_at\":\"${TOMORROW}T10:00:00\",\"reason\":\"Lab results\"}"

# Move the morning through the day: completed, checked in, no-show.
curl -sS -o /dev/null -X PUT "$BASE_URL/api/appointments/1" -H 'Content-Type: application/json' -d '{"status":"COMPLETED"}'
curl -sS -o /dev/null -X PUT "$BASE_URL/api/appointments/2" -H 'Content-Type: application/json' -d '{"status":"CHECKED_IN"}'
curl -sS -o /dev/null -X PUT "$BASE_URL/api/appointments/3" -H 'Content-Type: application/json' -d '{"status":"NO_SHOW"}'
echo "Seeded demo appointments for $TODAY"
