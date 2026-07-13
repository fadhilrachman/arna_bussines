from collections import defaultdict

from django.conf import settings
from django.db import transaction
from django.db.models import Sum

from .models import (
    Achievement,
    ChecklistCompletion,
    ChecklistItem,
    Goal,
    ScoreSnapshot,
    VaultDocument,
    XPTransaction,
)


SCORE_RULES = [
    ("digital.website_published", "Digital Presence", 20, "website_published"),
    ("digital.domain_connected", "Digital Presence", 20, "domain_connected"),
    ("digital.ssl_active", "Digital Presence", 15, "ssl_active"),
    ("legal.nib_uploaded", "Legal", 25, "nib_uploaded"),
    ("legal.npwp_uploaded", "Legal", 25, "npwp_uploaded"),
    ("finance.first_income", "Financial", 15, "first_income"),
    ("finance.first_expense", "Financial", 15, "first_expense"),
    ("finance.cashflow_ready", "Financial", 25, "cashflow_ready"),
    ("operation.sop_sales", "Operations", 20, "sop_sales"),
    ("operation.sop_purchase", "Operations", 15, "sop_purchase"),
    ("growth.goal_created", "Growth Readiness", 15, "goal_created"),
    ("growth.monthly_review", "Growth Readiness", 20, "monthly_review"),
]


def tenant_kwargs(context) -> dict:
    return {
        "organization_id": context.organization_id,
        "tenant_id": context.tenant_id,
    }


def stamp_create(serializer, context):
    serializer.save(
        organization_id=context.organization_id,
        tenant_id=context.tenant_id,
        created_by=context.user_id,
        updated_by=context.user_id,
    )


def calculate_level(total_xp: int) -> dict:
    thresholds = [
        (0, "Level 1", "Start"),
        (100, "Level 2", "Organize"),
        (300, "Level 3", "Grow"),
        (650, "Level 4", "Scale Up"),
        (1100, "Level 5", "Established"),
        (1800, "Level 6", "Corporate Ready"),
    ]
    current = thresholds[0]
    next_threshold = None
    for index, threshold in enumerate(thresholds):
        if total_xp >= threshold[0]:
            current = threshold
            next_threshold = thresholds[index + 1][0] if index + 1 < len(thresholds) else None
    progress = 100 if next_threshold is None else round((total_xp - current[0]) / (next_threshold - current[0]) * 100)
    return {
        "level": current[1],
        "level_name": current[2],
        "xp": total_xp,
        "next_xp": next_threshold,
        "progress_percent": max(0, min(progress, 100)),
    }


@transaction.atomic
def complete_checklist_item(context, item: ChecklistItem, evidence_file_id: str = "", note: str = ""):
    completion, _ = ChecklistCompletion.objects.get_or_create(
        organization_id=context.organization_id,
        tenant_id=context.tenant_id,
        item=item,
        defaults={
            "created_by": context.user_id,
            "updated_by": context.user_id,
            "evidence_file_id": evidence_file_id,
            "note": note,
        },
    )
    XPTransaction.objects.get_or_create(
        organization_id=context.organization_id,
        tenant_id=context.tenant_id,
        source_type="checklist_item",
        source_id=str(item.id),
        defaults={
            "created_by": context.user_id,
            "updated_by": context.user_id,
            "amount": item.xp_reward,
            "reason": f"Completed: {item.title}",
        },
    )
    unlock_achievements(context)
    return completion


def build_score_facts(context) -> dict:
    tenant = tenant_kwargs(context)
    document_types = set(VaultDocument.objects.filter(**tenant).values_list("document_type", flat=True))
    checklist_keys = set(
        ChecklistCompletion.objects.filter(**tenant).values_list("item__key", flat=True)
    )
    return {
        "nib_uploaded": "nib" in document_types,
        "npwp_uploaded": "npwp" in document_types,
        "sop_sales": "sop-sales" in checklist_keys,
        "sop_purchase": "sop-purchase" in checklist_keys,
        "monthly_review": "monthly-review" in checklist_keys,
        "goal_created": Goal.objects.filter(**tenant, status="active").exists(),
        "website_published": "website-published" in checklist_keys,
        "domain_connected": "domain-connected" in checklist_keys,
        "ssl_active": "ssl-active" in checklist_keys,
        "first_income": "first-income" in checklist_keys,
        "first_expense": "first-expense" in checklist_keys,
        "cashflow_ready": "cashflow-ready" in checklist_keys,
    }


@transaction.atomic
def recalculate_score(context) -> ScoreSnapshot:
    facts = build_score_facts(context)
    dimensions = defaultdict(int)
    explanation = []
    for key, dimension, points, fact_key in SCORE_RULES:
        earned = points if facts.get(fact_key) else 0
        dimensions[dimension] += earned
        explanation.append({"rule": key, "dimension": dimension, "points": earned, "max_points": points})
    overall = min(sum(dimensions.values()), 100)
    return ScoreSnapshot.objects.create(
        organization_id=context.organization_id,
        tenant_id=context.tenant_id,
        created_by=context.user_id,
        updated_by=context.user_id,
        version=settings.SCORE_CALCULATION_VERSION,
        overall_score=overall,
        dimensions=dict(dimensions),
        explanation=explanation,
    )


def unlock_achievements(context):
    tenant = tenant_kwargs(context)
    completed_count = ChecklistCompletion.objects.filter(**tenant).count()
    xp_value = XPTransaction.objects.filter(**tenant).aggregate(total=Sum("amount"))["total"] or 0
    candidates = []
    if completed_count >= 1:
        candidates.append(("first-step", "Langkah Pertama", "Checklist pertama selesai."))
    if completed_count >= 5:
        candidates.append(("operator-ready", "Operator Ready", "Lima checklist bisnis selesai."))
    if xp_value >= 300:
        candidates.append(("growth-runner", "Growth Runner", "Mencapai 300 XP."))
    for key, title, description in candidates:
        Achievement.objects.get_or_create(
            organization_id=context.organization_id,
            tenant_id=context.tenant_id,
            key=key,
            defaults={
                "created_by": context.user_id,
                "updated_by": context.user_id,
                "title": title,
                "description": description,
            },
        )


def xp_sum(context) -> int:
    return XPTransaction.objects.filter(**tenant_kwargs(context)).aggregate(total=Sum("amount"))["total"] or 0
