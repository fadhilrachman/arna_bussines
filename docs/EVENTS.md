# Events

Pulsar is planned for cross-service facts and async side effects. MVP keeps synchronous APIs and database state, with the following event contracts reserved.

## Consumed

- `website.site_published`
- `website.domain_connected`
- `website.ssl_active`
- `accounting.income_created`
- `accounting.expense_created`
- `accounting.cashflow_summary_ready`
- `file_manager.file_deleted`
- `commerce.entitlement_changed`

## Produced

- `business_hub.checklist_completed`
- `business_hub.xp_awarded`
- `business_hub.score_recalculated`
- `business_hub.achievement_unlocked`
- `business_hub.ai_insight_generated`

Events must include `organization_id`, `tenant_id`, `user_id`, `request_id`, `occurred_at`, and an idempotency key when they trigger mutations.
