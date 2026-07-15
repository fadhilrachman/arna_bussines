# Feedback Integration Status

Cross-check FE sidebar menu vs backend contract has been integrated.

## Previously Missing Endpoints

| Menu FE | Status | Endpoint |
| --- | --- | --- |
| SOP Library | Integrated | `GET /api/v1/business-hub/assets/sop/?tenant_id=...` |
| Templates | Integrated | `GET /api/v1/business-hub/assets/templates/?tenant_id=...` |
| Settings preferences | Integrated | `GET /api/v1/business-hub/settings/?tenant_id=...`, `PATCH /api/v1/business-hub/settings/?tenant_id=...` |
| Entitlements | Integrated | `GET /api/v1/business-hub/entitlements/?tenant_id=...` |

## Notes

- `GET /api/v1/business-hub/assets/?tenant_id=...` returns all active SOP/template catalog items.
- `GET /api/v1/business-hub/assets/?tenant_id=...&asset_type=sop` filters SOP assets.
- `GET /api/v1/business-hub/assets/?tenant_id=...&asset_type=template` filters template assets.
- Cloning SOP/template items into Business Vault remains backed by `POST /api/v1/business-hub/vault/documents/?tenant_id=...`.
- Business profile data in Settings remains backed by `/profiles/`; `/settings/` covers tenant preferences only.

## Existing Backed Menus

- Overview -> `/overview/`
- Roadmap -> `/roadmap/`
- Checklist -> `/roadmap/flat_checklist/` + `/checklist/completions/`
- Documents / Vault -> `/vault/documents/`
- Goals -> `/goals/`
- Calendar -> `/calendar/events/`
- AI Advisor -> `/ai/insights/`
- Achievements -> `/achievements/`

Summary: SOP Library, Templates, Settings preferences, and Entitlements are no longer dummy-only areas.
