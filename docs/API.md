# API

Base path: `/api/v1/business-hub/`

Interactive API documentation:

- Swagger UI: `/api/docs/`
- ReDoc: `/api/redoc/`
- OpenAPI schema: `/api/schema/`

Use tenant headers in local development:

```http
X-Organization-Id: org_demo
X-Tenant-Id: tenant_demo
X-User-Id: user_demo
X-Plan: free
```

## Dashboard

`GET /overview/`

Returns profile, level/XP, latest score snapshot, today quests, integrations, achievements, and quick action keys.

## Roadmap

`GET /roadmap/`

Returns seeded roadmap stages.

`GET /roadmap/flat_checklist/`

Returns checklist items with completion status for the current tenant.

## Checklist

`POST /checklist/completions/`

```json
{
  "item": 1,
  "evidence_file_id": "file_123",
  "note": "Uploaded NIB"
}
```

Completion is tenant-scoped and XP award is idempotent.

## Score

`POST /score/snapshots/recalculate/`

Creates a new Business Score snapshot from current facts.

## Vault

`POST /vault/documents/`

Stores metadata and File Manager `file_id`; it does not upload file bytes.
