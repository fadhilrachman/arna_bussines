from django.core.management.base import BaseCommand

from business_hub.models import ChecklistItem, RoadmapStage


STAGES = [
    ("start", 1, "Start", "Business identity exists and basic profile is complete.", 0, False),
    ("organize", 2, "Organize", "Legal, finance, and operational basics are documented.", 100, False),
    ("grow", 3, "Grow", "Website, customer tracking, and cashflow visibility are active.", 300, False),
    ("scale-up", 4, "Scale Up", "SOP, reporting, team role, and repeatable process exist.", 650, False),
    ("established", 5, "Established", "Governance, KPI, reporting, and readiness documents exist.", 1100, False),
    ("corporate-ready", 6, "Corporate Ready", "Compliance, funding readiness, and management structure are mature.", 1800, False),
    ("enterprise-ready", 7, "Enterprise Ready", "Future advanced auditability, integrations, branches, and controls.", 2600, True),
]

CHECKLIST = [
    ("complete-profile", "start", "Lengkapi profil bisnis", "Identity and Digital Presence", "profile_field", 25, "Digital Presence", False),
    ("website-published", "start", "Publikasikan website bisnis", "Identity and Digital Presence", "website_status", 40, "Digital Presence", False),
    ("domain-connected", "grow", "Hubungkan domain custom", "Identity and Digital Presence", "website_status", 35, "Digital Presence", True),
    ("ssl-active", "grow", "Aktifkan SSL website", "Identity and Digital Presence", "website_status", 20, "Digital Presence", False),
    ("nib-uploaded", "organize", "Unggah NIB ke Business Vault", "Legal and Compliance", "file_evidence", 35, "Legal", False),
    ("npwp-uploaded", "organize", "Unggah NPWP ke Business Vault", "Legal and Compliance", "file_evidence", 35, "Legal", False),
    ("first-income", "organize", "Catat pemasukan pertama", "Financial Management", "accounting_fact", 20, "Financial", False),
    ("first-expense", "organize", "Catat pengeluaran pertama", "Financial Management", "accounting_fact", 20, "Financial", False),
    ("cashflow-ready", "grow", "Tinjau ringkasan cashflow", "Financial Management", "accounting_fact", 35, "Financial", True),
    ("sop-sales", "scale-up", "Buat SOP penjualan", "Operations and SOP", "manual_checklist", 35, "Operations", False),
    ("sop-purchase", "scale-up", "Buat SOP pembelian", "Operations and SOP", "manual_checklist", 30, "Operations", False),
    ("monthly-review", "established", "Selesaikan review bisnis bulanan", "Growth and Readiness", "manual_checklist", 30, "Growth Readiness", False),
]


class Command(BaseCommand):
    help = "Seed repeatable roadmap stages and default checklist items."

    def handle(self, *args, **options):
        stages = {}
        for key, order, name, definition, xp_required, is_future in STAGES:
            stage, _ = RoadmapStage.objects.update_or_create(
                key=key,
                defaults={
                    "order": order,
                    "name": name,
                    "definition": definition,
                    "xp_required": xp_required,
                    "is_future": is_future,
                },
            )
            stages[key] = stage

        for key, stage_key, title, category, requirement_type, xp_reward, score_dimension, is_premium in CHECKLIST:
            ChecklistItem.objects.update_or_create(
                key=key,
                defaults={
                    "stage": stages[stage_key],
                    "title": title,
                    "category": category,
                    "requirement_type": requirement_type,
                    "xp_reward": xp_reward,
                    "score_dimension": score_dimension,
                    "is_premium": is_premium,
                },
            )
        self.stdout.write(self.style.SUCCESS("Business Hub roadmap and checklist seed completed."))
