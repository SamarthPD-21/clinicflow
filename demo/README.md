# Demo

| File | What it is |
|---|---|
| [`ClinicFlow-Demo.mp4`](ClinicFlow-Demo.mp4) | Recorded walkthrough (7 min, 1080p) |
| [`ClinicFlow-DevOps-Capstone.pptx`](ClinicFlow-DevOps-Capstone.pptx) | Presentation slides (15 slides, speaker notes included) |

## What the video shows

1. **0:00 – Intro:** what ClinicFlow does and the commit → production pipeline.
2. **0:24 – Live app on Kubernetes (kind, via ingress-nginx):** dashboard, booking an appointment,
   the API rejecting a double-booking with 409, appointments / doctors / patients views, the mobile
   layout, Swagger, Prometheus targets and a query, the Grafana dashboard, GitHub Actions runs and the
   SHA-tagged images in GHCR.
3. **2:04 – Each module with its evidence:** API and database, pytest, git history, Docker Compose, the
   CI pipeline, Trivy blocking CVE-2025-62727, Terraform plan / apply / AWS Console / EKS / destroy,
   `kubectl` + `helm list` + Ingress, the HPA scaling 2 → 6, metrics / Prometheus / Grafana, the
   commit → pipeline → `helm upgrade` demo, and the three troubleshooting scenarios.
4. **6:56 – What I learned.**

Every screenshot in the video is also in [`docs/screenshots/`](../docs/screenshots/), mapped to the
grading rubric in [`docs/SUBMISSION.md`](../docs/SUBMISSION.md).
