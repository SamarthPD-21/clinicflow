# ClinicFlow

[![CI/CD](https://github.com/SamarthPD-21/clinicflow/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/SamarthPD-21/clinicflow/actions/workflows/ci-cd.yml)

ClinicFlow is a front-desk appointment system for small clinics. Reception staff can register patients,
manage the doctors on duty, book appointments, and move each visit through the day
(scheduled → checked in → completed / cancelled / no-show). The API refuses to double-book a doctor
inside the same 30-minute slot.

This is my DevOps capstone project. The app is deliberately small; the point is the path it takes from
a commit on my laptop to a monitored, autoscaled deployment on Kubernetes.

```text
 git push ─▶ GitHub Actions ─▶ pytest + ruff ─▶ docker build ─▶ Trivy scan ─▶ GHCR (tag = commit SHA)
                                                                                   │
                         CI bumps image tag in helm/clinicflow/values.yaml ◀───────┘
                                          │
                         helm upgrade --install ─▶ Kubernetes (kind locally / EKS on AWS via Terraform)
                                                         │
                ┌──────────── ingress-nginx ─────────────┤
                │  /      ─▶ frontend (React + nginx) x2 │
                │  /api   ─▶ backend (FastAPI) x2..6 HPA │──▶ PostgreSQL (StatefulSet + PVC)
                └────────────────────────────────────────┘
                                          │ /metrics
                              Prometheus ─▶ Grafana dashboard
```

## Stack

| Layer | Tooling |
|---|---|
| Frontend | React 18 + Vite, plain CSS (responsive), served by `nginx-unprivileged` |
| Backend | FastAPI, SQLAlchemy 2, Alembic migrations, Pydantic |
| Database | PostgreSQL 16 |
| Tests | pytest (22 tests, in-memory SQLite, no production DB), ruff |
| Containers | Multi-stage Dockerfiles, non-root users, Docker Compose |
| CI/CD | GitHub Actions → GHCR, SHA image tags, Helm deploy (Argo CD manifest optional) |
| Security | Trivy image scan, build fails on fixable HIGH/CRITICAL CVEs |
| Infra as code | Terraform: AWS VPC (2 public + 2 private subnets, NAT) + EKS with managed node group |
| Kubernetes | Helm chart: Deployments, Services, StatefulSet, Ingress, HPA, ServiceMonitor |
| Observability | kube-prometheus-stack (Prometheus + Grafana), custom dashboard |

## Repository layout

```text
backend/            FastAPI app, Alembic migrations, pytest suite, Dockerfile
frontend/           React app, nginx config template, multi-stage Dockerfile
docker-compose.yml  postgres + backend + frontend, one command
.github/workflows/  CI/CD pipeline
terraform/          AWS VPC + EKS
helm/clinicflow/    Helm chart (+ Grafana dashboard JSON)
k8s/                namespace, kind cluster config, Argo CD Application, EKS StorageClass
monitoring/         kube-prometheus-stack values
troubleshooting/    deliberately broken manifests + runbook
scripts/            demo data seeding and load generation
docs/               submission notes and screenshots
```

## API

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Liveness – process is up |
| GET | `/ready` | Readiness – database reachable (503 otherwise) |
| GET | `/metrics` | Prometheus metrics |
| GET/POST | `/api/doctors` | List (filter `?active=`) / add doctors |
| GET/PUT/DELETE | `/api/doctors/{id}` | Read / update / remove a doctor |
| GET/POST | `/api/patients` | List (search `?q=`) / register patients |
| GET/PUT/DELETE | `/api/patients/{id}` | Read / update / remove a patient |
| GET/POST | `/api/appointments` | List (filter `?day=&status=&doctor_id=`) / book (409 on slot clash) |
| GET/PUT/DELETE | `/api/appointments/{id}` | Read / reschedule or change status / delete |
| GET | `/api/appointments/stats` | Dashboard numbers |

Interactive docs: `http://localhost:8000/docs`.

## Run it locally

```bash
docker compose up --build          # postgres, backend (runs migrations), frontend
./scripts/seed-demo.sh             # optional: book a day of demo appointments
```

- App: http://localhost:3000
- API docs: http://localhost:8000/docs
- `docker compose down -v` stops everything and drops the database volume.

Backend without Docker (needs a Postgres):

```bash
cd backend
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
export DATABASE_URL=postgresql+psycopg://clinicflow:clinicflow@localhost:5432/clinicflow
alembic upgrade head
uvicorn app.main:app --reload
```

Frontend dev server: `cd frontend && npm ci && npm run dev` (proxies `/api` to `localhost:8000`).

## Tests

```bash
cd backend && pytest -v
```

`tests/conftest.py` swaps the database dependency for an in-memory SQLite engine, so tests never touch
Postgres. They cover CRUD on all three resources, validation errors, the double-booking rule
(overlapping, back-to-back, cancelled slot, rescheduling into a taken slot), stats, and `/metrics`.

## CI/CD

`.github/workflows/ci-cd.yml` runs on every push and PR to `main`:

1. **test** – ruff, pytest (fails the build on any failure), `npm ci && npm run build`.
2. **build-scan-push** (backend + frontend in parallel) – `docker build`, Trivy scan with
   `--severity HIGH,CRITICAL --ignore-unfixed --exit-code 1`, then push
   `ghcr.io/samarthpd-21/clinicflow-{backend,frontend}:<commit-sha>`. Nothing is pushed if the scan fails,
   and PRs build + scan but never push.
3. **deploy** – rewrites the two image tags in `helm/clinicflow/values.yaml` to the new SHA and commits,
   so `main` always describes what should be running. If a `KUBE_CONFIG_DATA` secret is set (a reachable
   cluster such as EKS), the job also runs `helm upgrade --install`. For the local kind cluster, which
   GitHub can't reach, `scripts/deploy.sh` pulls `main` and runs the same Helm upgrade.
   (`k8s/argocd-application.yaml` is an optional GitOps alternative: Argo CD watches the chart and syncs
   on every tag bump, at the cost of no `helm list` release.)

Images are never tagged `latest` by CI, so every running pod traces back to one commit.

## Kubernetes (local, kind)

```bash
kind create cluster --config k8s/kind/cluster.yaml
kubectl apply -f k8s/namespace.yaml

# ingress controller + metrics-server (for HPA)
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.13.3/deploy/static/provider/kind/deploy.yaml
# kind only maps host ports 80/443 on the control-plane node, so pin the controller there
kubectl patch deploy ingress-nginx-controller -n ingress-nginx --type merge -p \
  '{"spec":{"template":{"spec":{"nodeSelector":{"kubernetes.io/hostname":"clinicflow-control-plane"},"tolerations":[{"key":"node-role.kubernetes.io/control-plane","operator":"Exists","effect":"NoSchedule"}]}}}}'
helm upgrade --install metrics-server metrics-server/metrics-server -n kube-system --set args={--kubelet-insecure-tls}

# monitoring (see monitoring/README.md)
helm upgrade --install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  -n monitoring --create-namespace -f monitoring/kube-prometheus-stack-values.yaml

# app: deploys the image SHA that CI last wrote into values.yaml
./scripts/deploy.sh          # = git pull + helm upgrade --install clinicflow ./helm/clinicflow -n clinicflow --wait
```

Add to `/etc/hosts`: `127.0.0.1 clinicflow.local grafana.clinicflow.local prometheus.clinicflow.local`,
then open http://clinicflow.local.

Useful checks:

```bash
kubectl get pods,svc,ingress,hpa -n clinicflow
helm list -n clinicflow
URL=http://clinicflow.local ./scripts/load-test.sh 30 180   # watch the HPA scale out
kubectl get hpa -n clinicflow -w
```

## AWS (Terraform + EKS)

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform plan -out tfplan
terraform apply tfplan                       # ~15 min
aws eks update-kubeconfig --region ap-south-1 --name clinicflow-dev-eks
kubectl apply -f ../k8s/eks/storageclass-gp3.yaml
# ingress-nginx (cloud provider manifest) then:
helm upgrade --install clinicflow ../helm/clinicflow -n clinicflow --create-namespace -f ../helm/clinicflow/values-eks.yaml

terraform destroy                            # always, when done
```

Creates a VPC (`10.20.0.0/16`, two public and two private subnets in two AZs, one NAT gateway), an EKS
1.34 control plane and a managed node group of 2 × t3.medium in the private subnets, with the EBS CSI
add-on so the Postgres PVC gets a gp3 volume. No credentials live in the repo – Terraform uses the AWS
CLI profile, and `*.tfvars` / state files are git-ignored.

## Monitoring

The backend exposes request count/latency histograms per route plus two domain metrics
(`clinicflow_appointments_booked_total{specialty}`, `clinicflow_booking_conflicts_total`). A
ServiceMonitor tells Prometheus to scrape it every 15 s, and the **ClinicFlow API** Grafana dashboard
(requests/s, p95 latency, 5xx ratio, per-endpoint traffic, per-pod CPU, bookings by specialty) is shipped
in the Helm chart as a ConfigMap. See `monitoring/README.md`.

## Troubleshooting lab

`troubleshooting/` contains three broken manifests (bad image tag, Service selector mismatch, wrong DB
password failing readiness) with the kubectl steps to diagnose and fix each one – see
`troubleshooting/README.md`.

## Design notes

- **`/health` vs `/ready`** – liveness only checks the process, readiness checks the database. A DB
  outage takes pods out of the Service instead of restart-looping them.
- **Migrations** – the backend container runs `alembic upgrade head` before starting. Several replicas
  start together, so `alembic/env.py` takes a Postgres advisory lock so only one migrates at a time.
- **Postgres in the cluster** – fine for a demo. In production I'd use Amazon RDS (backups, Multi-AZ,
  patching) and point `DATABASE_URL` at it via `postgres.existingSecret`.
- **Non-root everywhere** – backend uid 10001, frontend uid 101 on port 8080, `allowPrivilegeEscalation:
  false` and all capabilities dropped in the pod specs.

Submission notes and screenshots: [`docs/SUBMISSION.md`](docs/SUBMISSION.md).
