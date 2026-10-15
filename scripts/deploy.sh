#!/usr/bin/env bash
# Deploy whatever images CI last built and scanned on main.
# CI's deploy job writes the commit SHA into helm/clinicflow/values.yaml, so pulling main is enough.
set -euo pipefail
cd "$(dirname "$0")/.."
git pull --ff-only --quiet origin main
echo "Deploying image tag: $(grep -m1 'tag:' helm/clinicflow/values.yaml | awk '{print $2}')"
helm upgrade --install clinicflow ./helm/clinicflow -n clinicflow --create-namespace --wait --timeout 5m "$@"
kubectl rollout status deploy/clinicflow-backend -n clinicflow
kubectl rollout status deploy/clinicflow-frontend -n clinicflow
helm history clinicflow -n clinicflow --max 5
