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

Local development memakai `DEV_AUTH_BYPASS=True` secara default saat `DEBUG=True`.
Semua endpoint Business Hub tetap wajib menerima `tenant_id` sebagai query parameter:

```http
GET /api/v1/business-hub/overview/?tenant_id=tenant_demo
```

Untuk mensimulasikan organization/user lain di local development, kirim header:

```http
X-Organization-Id: org_demo
X-User-Id: user_demo
X-Plan: free
```

## Main Endpoints

- `GET /health/live`
- `GET /health/ready`
- `GET /api/schema/`
- `GET /api/v1/business-hub/overview/?tenant_id=tenant_demo`
- `GET /api/v1/business-hub/roadmap/?tenant_id=tenant_demo`
- `GET /api/v1/business-hub/roadmap/flat_checklist/?tenant_id=tenant_demo`
- `POST /api/v1/business-hub/checklist/completions/?tenant_id=tenant_demo`
- `POST /api/v1/business-hub/score/snapshots/recalculate/?tenant_id=tenant_demo`
- `GET|POST /api/v1/business-hub/vault/documents/?tenant_id=tenant_demo`
- `GET|POST /api/v1/business-hub/goals/?tenant_id=tenant_demo`
- `GET|POST /api/v1/business-hub/calendar/events/?tenant_id=tenant_demo`
- `GET|POST /api/v1/business-hub/ai/insights/?tenant_id=tenant_demo`

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
