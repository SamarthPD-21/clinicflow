# Monitoring

| Piece | Where |
|---|---|
| App metrics | `GET /metrics` on the backend (prometheus-fastapi-instrumentator + custom booking counters) |
| Scrape config | `ServiceMonitor` in `helm/clinicflow/templates/servicemonitor.yaml` |
| Prometheus + Grafana | `kube-prometheus-stack`, values in `kube-prometheus-stack-values.yaml` |
| Dashboard | `helm/clinicflow/dashboards/clinicflow.json`, shipped as a ConfigMap and auto-loaded by the Grafana sidecar |

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm upgrade --install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  -n monitoring --create-namespace -f monitoring/kube-prometheus-stack-values.yaml

# Grafana admin password
kubectl get secret -n monitoring kube-prometheus-stack-grafana -o jsonpath='{.data.admin-password}' | base64 -d; echo
```

Open http://grafana.clinicflow.local (dashboard **ClinicFlow API**) and http://prometheus.clinicflow.local/targets.

Custom metrics:

- `clinicflow_appointments_booked_total{specialty}` – bookings per specialty
- `clinicflow_booking_conflicts_total` – requests rejected with 409 because the doctor was already booked
