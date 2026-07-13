# Arna Business Hub

Business Hub Service untuk ekosistem Bisnis Naik Kelas. Service ini mengorkestrasi roadmap, checklist, Business Vault metadata, skor kesiapan, gamification, goals, calendar, AI insight metadata, dan status integrasi lintas service.

## Local Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd source
python manage.py migrate
python manage.py seed_business_hub
python manage.py runserver 0.0.0.0:8000
```

Di Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd source
python manage.py migrate
python manage.py seed_business_hub
python manage.py runserver 0.0.0.0:8000
```

Local development memakai `DEV_AUTH_BYPASS=True` secara default saat `DEBUG=True`. Untuk mensimulasikan tenant lain, kirim header:

```http
X-Organization-Id: org_demo
X-Tenant-Id: tenant_demo
X-User-Id: user_demo
X-Plan: free
```

## Main Endpoints

- `GET /health/live`
- `GET /health/ready`
- `GET /api/schema/`
- `GET /api/v1/business-hub/overview/`
- `GET /api/v1/business-hub/roadmap/`
- `GET /api/v1/business-hub/roadmap/flat_checklist/`
- `POST /api/v1/business-hub/checklist/completions/`
- `POST /api/v1/business-hub/score/snapshots/recalculate/`
- `GET|POST /api/v1/business-hub/vault/documents/`
- `GET|POST /api/v1/business-hub/goals/`
- `GET|POST /api/v1/business-hub/calendar/events/`
- `GET|POST /api/v1/business-hub/ai/insights/`

## Scope Implemented

This repository is an MVP backend scaffold based on the PRD:

- Django/DRF service structure
- Tenant-scoped models and APIs
- Roadmap/checklist seed
- Checklist completion with idempotent XP
- Basic Business Score v1
- Business Vault metadata storing `file_id` only
- Free/Premium gates for sample premium actions
- Health checks, OpenAPI schema endpoint, Dockerfile, Jenkinsfile
- Docs for architecture, API, events, score engine, and frontend integration
