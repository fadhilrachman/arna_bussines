# Architecture

Business Hub owns the guided business growth layer for Bisnis Naik Kelas. It stores tenant-scoped metadata for profile, roadmap progress, checklist completion, vault document references, score snapshots, goals, calendar events, achievements, XP, integration status, and AI insight metadata.

It does not own authentication, subscriptions, object storage, accounting transactions, website publishing, notification delivery, or model inference. Those boundaries remain with SSO, Commerce, File Manager, SME Accounting, Website Service, Notification Service, and AI Gateway.

## Runtime

- Backend: Django + Django REST Framework
- Database: PostgreSQL in deployment, SQLite for local development when `POSTGRES_HOST` is absent
- Cache/jobs: Redis/Celery placeholder for later phases
- Events: Pulsar placeholder for later integration phases
- API: HTTP JSON under `/api/v1/business-hub/`

## Tenant Context

Current MVP uses `TenantContextMiddleware` as a stable contract for views/services. In development it accepts headers. Production work should replace the trust boundary with SSO JWT validation while keeping `request.business_context` unchanged.

## Service Boundaries

- File uploads: create file in File Manager, then store only `file_id` in `VaultDocument`
- Website facts: consume published/domain/SSL state through Website Service APIs/events
- Accounting facts: consume summary/facts, never accounting rows directly
- AI: send sanitized context to AI Gateway, store recommendation metadata only
- Commerce: enforce entitlements server-side before gated mutations
