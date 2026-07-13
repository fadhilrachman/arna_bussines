# Frontend Integration

Business Hub should be integrated into the existing Bisnis Naik Kelas dashboard instead of shipped as a separate UI.

Screens from the PRD:

- Overview
- Roadmap
- Checklist
- Documents / Vault
- SOP Library
- Templates
- Goals
- Calendar
- AI Advisor
- Achievements
- Settings

The first production slice should call `GET /api/v1/business-hub/overview/` and render:

- Level, level name, XP progress, and next milestone
- Business Score panel
- Roadmap path summary
- Today Quest list with XP reward
- Integration status list
- Recent achievements
- Quick action buttons

Frontend must display entitlement results from the backend but must not be the source of enforcement.
