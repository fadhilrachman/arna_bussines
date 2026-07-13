# Score Engine

Business Score v1 follows the PRD seed rules. Current implementation calculates facts from tenant-owned checklist completion, vault document metadata, and goals. Later integration phases should enrich facts from Website Service and SME Accounting APIs/events.

Dimensions:

- Digital Presence
- Legal
- Financial
- Operations
- Growth Readiness

Score snapshots are immutable. Recalculation creates a new `ScoreSnapshot` with `version`, `overall_score`, `dimensions`, and `explanation`.
