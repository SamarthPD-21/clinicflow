# Troubleshooting lab

Each manifest breaks one thing on purpose. Apply it, diagnose with kubectl, fix, delete.

## 1. Bad image tag → `ImagePullBackOff`

```bash
kubectl apply -f troubleshooting/broken-image.yaml
kubectl get pods -n clinicflow -l app=clinicflow-broken-image
kubectl describe pod -n clinicflow -l app=clinicflow-broken-image | tail -15
kubectl get events -n clinicflow --sort-by=.lastTimestamp | tail
```

Events show `Failed to pull image ... not found`. Fix: point the image at a tag that exists
(`kubectl set image deploy/clinicflow-broken-image backend=ghcr.io/samarthpd-21/clinicflow-backend:<sha>`).

## 2. Selector mismatch → Service with no endpoints

```bash
kubectl apply -f troubleshooting/broken-service.yaml
kubectl get endpointslices -n clinicflow -l kubernetes.io/service-name=clinicflow-backend-broken
kubectl get svc clinicflow-backend-broken -n clinicflow -o jsonpath='{.spec.selector}'; echo
kubectl get pods -n clinicflow --show-labels | grep backend
```

The selector says `app=clinicflow-api` but pods carry `app=clinicflow-backend`. No matching labels → no
endpoints → no traffic. Fix the selector:
`kubectl patch svc clinicflow-backend-broken -n clinicflow -p '{"spec":{"selector":{"app":"clinicflow-backend"}}}'`.

## 3. Wrong DB credentials → Running but not Ready

```bash
kubectl apply -f troubleshooting/broken-readiness.yaml
kubectl get pods -n clinicflow -l app=clinicflow-broken-readiness     # READY 0/1
kubectl describe pod -n clinicflow -l app=clinicflow-broken-readiness | grep -A3 Readiness
kubectl logs -n clinicflow -l app=clinicflow-broken-readiness | tail
```

Liveness (`/health`) would pass, but readiness (`/ready`) runs `SELECT 1` and returns 503, so the pod
never receives traffic. Fix: read credentials from the `clinicflow-postgres` secret, as the Helm chart does.

## Clean up

```bash
kubectl delete -f troubleshooting/ --ignore-not-found
```
