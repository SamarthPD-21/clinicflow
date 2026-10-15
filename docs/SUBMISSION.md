# Capstone submission – ClinicFlow

- **Repository:** https://github.com/SamarthPD-21/clinicflow
- **Pipeline runs:** https://github.com/SamarthPD-21/clinicflow/actions
- **Images:** `ghcr.io/samarthpd-21/clinicflow-backend`, `ghcr.io/samarthpd-21/clinicflow-frontend` (public, tagged with commit SHA)

All screenshots are in [`docs/screenshots/`](screenshots/). File names start with the rubric module.

## M1 – Application

| Requirement | Evidence |
|---|---|
| FastAPI `/health` | `backend/app/main.py`, [m8-ingress-curl](screenshots/m8-ingress-curl.png), [m4-docker-images-nonroot](screenshots/m4-docker-images-nonroot.png) |
| ≥ 4 REST endpoints (GET/POST/PUT/DELETE) | `backend/app/routers/` – 15 endpoints over doctors, patients, appointments. [m1-swagger-docs](screenshots/m1-swagger-docs.png), [m1-api-crud-curl](screenshots/m1-api-crud-curl.png) |
| PostgreSQL + Alembic | `backend/alembic/versions/0001_initial_schema.py`, `0002_seed_demo_data.py`. [m1-database-tables](screenshots/m1-database-tables.png) |
| Frontend calls the API | [m1-dashboard-ingress](screenshots/m1-dashboard-ingress.png), [m1-appointments-table](screenshots/m1-appointments-table.png), [m1-booking-success](screenshots/m1-booking-success.png), [m1-booking-conflict-409](screenshots/m1-booking-conflict-409.png), [m1-doctors](screenshots/m1-doctors.png), [m1-patients](screenshots/m1-patients.png) |
| Responsive UI | [m1-mobile-responsive](screenshots/m1-mobile-responsive.png), [m10-demo-4-mobile-after-deploy](screenshots/m10-demo-4-mobile-after-deploy.png) |

## M2 – Testing

22 pytest tests across `/health`, `/ready`, `/metrics`, doctors, patients and appointments.
`tests/conftest.py` overrides the DB dependency with in-memory SQLite, so the production database is never used.
`backend/pytest.ini` configures the run.

[m2-pytest-verbose](screenshots/m2-pytest-verbose.png) · [m2-ruff-lint](screenshots/m2-ruff-lint.png)

## M3 – Git and GitHub

Public repo, 20+ commits, `.gitignore` covers `.env`, `__pycache__`, `node_modules`, `.venv`, Terraform state and tfvars.

[m3-git-log](screenshots/m3-git-log.png) · [m3-github-commit-history](screenshots/m3-github-commit-history.png) · [m3-gitignore](screenshots/m3-gitignore.png)

## M4 – Docker

- `backend/Dockerfile` – python:3.12-slim, runs as uid 10001, healthcheck, migrations then uvicorn.
- `frontend/Dockerfile` – multi-stage: `node:22-alpine` build → `nginx-unprivileged` runtime (uid 101, port 8080).
- `docker-compose.yml` – postgres + backend + frontend with health-gated startup.

[m4-docker-compose-up](screenshots/m4-docker-compose-up.png) · [m4-compose-localhost-3000](screenshots/m4-compose-localhost-3000.png) · [m4-docker-images-nonroot](screenshots/m4-docker-images-nonroot.png)

## M5 – CI/CD

`.github/workflows/ci-cd.yml`: on push to `main` → ruff + pytest (build fails on test failure) → frontend build →
build both images → Trivy → push to GHCR tagged `<commit-sha>` → write the SHA into `helm/clinicflow/values.yaml`.

[m5-actions-run-green](screenshots/m5-actions-run-green.png) · [m5-actions-history](screenshots/m5-actions-history.png) ·
[m5-ghcr-packages](screenshots/m5-ghcr-packages.png) · [m5-ghcr-backend-sha-tags](screenshots/m5-ghcr-backend-sha-tags.png) · [m5-ghcr-frontend-sha-tags](screenshots/m5-ghcr-frontend-sha-tags.png)

## M6 – Trivy

The scan step runs `aquasec/trivy:0.76.0 image --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1` on both images
before anything is pushed.

[m6-trivy-pipeline-backend](screenshots/m6-trivy-pipeline-backend.png) · [m6-trivy-pipeline-frontend](screenshots/m6-trivy-pipeline-frontend.png) · [m6-trivy-gate-blocks-old-starlette](screenshots/m6-trivy-gate-blocks-old-starlette.png)

**What it scanned and what the result means.** Trivy inspected every OS package in the image (Debian for the
backend, Alpine for the frontend) and every Python package installed in site-packages, and compared versions against
its vulnerability database. The current images report 0 HIGH/CRITICAL issues with a fix available, so the gate
passes and the images are pushed. It did catch real problems while I was building this: FastAPI 0.115.6 pulled in
Starlette 0.41.3, which has **CVE-2025-62727** – a denial of service where a crafted HTTP `Range` header makes
Starlette spend excessive CPU merging byte ranges – so I upgraded to FastAPI 0.143 / Starlette 1.8. The nginx
Alpine base also had 43 fixable HIGH CVEs (curl, OpenSSL, c-ares), fixed by running `apk upgrade` in the Dockerfile.
The scan does not prove the app is secure; it only covers known CVEs in packaged software.

## M7 – Terraform (AWS)

`terraform/` – VPC (2 public + 2 private subnets across 2 AZs, NAT gateway) and EKS 1.34 with a managed node group
(2 × c7i-flex.large), EBS CSI add-on. `terraform.tfvars.example` is committed; no credentials are in the repo.

[m7-terraform-init-validate](screenshots/m7-terraform-init-validate.png) · [m7-terraform-plan](screenshots/m7-terraform-plan.png) ·
[m7-terraform-apply](screenshots/m7-terraform-apply.png) · [m7-aws-console-vpc](screenshots/m7-aws-console-vpc.png) ·
[m7-aws-console-eks](screenshots/m7-aws-console-eks.png) · [m7-aws-cli-vpc-eks](screenshots/m7-aws-cli-vpc-eks.png) ·
[m7-terraform-destroy](screenshots/m7-terraform-destroy.png)

The app was also deployed to the EKS cluster with the same Helm chart (`-f values-eks.yaml`, Postgres on a gp3 EBS
volume): [m7-eks-kubectl-nodes-pods](screenshots/m7-eks-kubectl-nodes-pods.png) ·
[m7-eks-app-via-ingress](screenshots/m7-eks-app-via-ingress.png) · [m7-eks-app-dashboard](screenshots/m7-eks-app-dashboard.png)

Two limits of the AWS Free plan account I hit:
- Only free-tier instance types can be launched. The first apply used `t3.medium` and the node group hung; CloudTrail
  showed `RunInstances ... not eligible for Free Tier`. I switched the nodes to `c7i-flex.large` (2 vCPU / 4 GiB) and
  re-applied, which replaced just the node group (`4 added, 1 destroyed` in the apply screenshot).
- The account can't create load balancers (`OperationNotPermitted`), so the ingress-nginx Service never got a public
  hostname. I reached the ingress controller with `kubectl port-forward` instead; the Ingress rules are the same.

Before `terraform destroy` I uninstalled the release and deleted the PVC so the EBS volume wasn't orphaned.

## M8 – Kubernetes + Helm

| Requirement | Evidence |
|---|---|
| `k8s/namespace.yaml` | [m8-namespace-apply](screenshots/m8-namespace-apply.png) |
| Helm chart (`helm/clinicflow`) | `Chart.yaml`, `values.yaml`, `templates/` |
| `helm upgrade --install` / `helm list` | [m8-helm-list](screenshots/m8-helm-list.png), [m10-demo-3-deploy-new-sha](screenshots/m10-demo-3-deploy-new-sha.png) |
| ≥ 2 replicas each, all Running | [m8-kubectl-get-pods](screenshots/m8-kubectl-get-pods.png), [m8-deployments-replicas](screenshots/m8-deployments-replicas.png) |
| ClusterIP Services | [m8-kubectl-get-svc-ingress](screenshots/m8-kubectl-get-svc-ingress.png) |
| Ingress `/` → frontend, `/api` → backend | [m8-deployments-replicas](screenshots/m8-deployments-replicas.png) (describe ingress), [m8-ingress-curl](screenshots/m8-ingress-curl.png), [m1-dashboard-ingress](screenshots/m1-dashboard-ingress.png) |
| HPA | [m8-hpa-scaled-under-load](screenshots/m8-hpa-scaled-under-load.png) (2 → 6 pods under load), [m8-hpa-after-load](screenshots/m8-hpa-after-load.png) |

## M9 – Observability

[m9-metrics-endpoint](screenshots/m9-metrics-endpoint.png) · [m9-servicemonitor](screenshots/m9-servicemonitor.png) ·
[m9-prometheus-targets-up](screenshots/m9-prometheus-targets-up.png) (6/6 backend pods UP) · [m9-prometheus-query-graph](screenshots/m9-prometheus-query-graph.png) ·
[m9-grafana-dashboard](screenshots/m9-grafana-dashboard.png)

## M10 – Demo: commit → pipeline → deployment

1. Commit `c1b5ead` ("fix mobile nav overflow and 5xx panel showing no data") pushed to `main`.
2. Pipeline runs: [m10-demo-1-pipeline-running](screenshots/m10-demo-1-pipeline-running.png) → [m5-actions-run-green](screenshots/m5-actions-run-green.png).
3. Cluster before: [m10-demo-2-before-deploy](screenshots/m10-demo-2-before-deploy.png).
4. `./scripts/deploy.sh` rolls both Deployments to `:c1b5ead…`: [m10-demo-3-deploy-new-sha](screenshots/m10-demo-3-deploy-new-sha.png).
5. Fix visible in the app: [m10-demo-4-mobile-after-deploy](screenshots/m10-demo-4-mobile-after-deploy.png).

## Troubleshooting

| Scenario | Diagnose | Fix |
|---|---|---|
| Bad image tag → ImagePullBackOff | [t1-broken-image-diagnose](screenshots/t1-broken-image-diagnose.png) | [t1-broken-image-fixed](screenshots/t1-broken-image-fixed.png) |
| Service selector mismatch → no endpoints | [t2-broken-service-diagnose](screenshots/t2-broken-service-diagnose.png) | [t2-broken-service-fixed](screenshots/t2-broken-service-fixed.png) |
| Wrong DB password → Running but not Ready | [t3-broken-readiness-diagnose](screenshots/t3-broken-readiness-diagnose.png) | see `troubleshooting/README.md` |
