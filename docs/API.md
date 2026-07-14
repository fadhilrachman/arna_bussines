# API

Base path: `/api/v1/business-hub/`

All Business Hub endpoints require `tenant_id` as a query parameter:

```http
?tenant_id=tenant_demo
```

Interactive API documentation:

- Swagger UI: `/api/docs/`
- ReDoc: `/api/redoc/`
- OpenAPI schema: `/api/schema/`

Use organization/user headers in local development:

```http
X-Organization-Id: org_demo
X-User-Id: user_demo
X-Plan: free
```

## Dashboard

`GET /overview/?tenant_id=tenant_demo`

Returns profile, level/XP, latest score snapshot, today quests, integrations, achievements, and quick action keys.

## Roadmap

`GET /roadmap/?tenant_id=tenant_demo`

Returns seeded roadmap stages.

`GET /roadmap/flat_checklist/?tenant_id=tenant_demo`

Returns checklist items with completion status for the current tenant.

## Checklist

`POST /checklist/completions/?tenant_id=tenant_demo`

```json
{
  "item": 1,
  "evidence_file_id": "file_123",
  "note": "Uploaded NIB"
}
```

Completion is tenant-scoped and XP award is idempotent.

## Score

`POST /score/snapshots/recalculate/?tenant_id=tenant_demo`

Creates a new Business Score snapshot from current facts.

## Vault

`POST /vault/documents/?tenant_id=tenant_demo`

Stores metadata and File Manager `file_id`; it does not upload file bytes.
