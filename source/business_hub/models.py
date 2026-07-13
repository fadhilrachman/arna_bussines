import uuid

from django.db import models
from django.utils import timezone


class TenantModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization_id = models.CharField(max_length=80, db_index=True)
    tenant_id = models.CharField(max_length=80, db_index=True)
    created_by = models.CharField(max_length=80, blank=True)
    updated_by = models.CharField(max_length=80, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class BusinessProfile(TenantModel):
    business_name = models.CharField(max_length=180)
    industry = models.CharField(max_length=120, blank=True)
    business_stage = models.CharField(max_length=80, default="Start")
    city = models.CharField(max_length=120, blank=True)
    phone = models.CharField(max_length=60, blank=True)
    website_url = models.URLField(blank=True)
    description = models.TextField(blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = [("organization_id", "tenant_id")]

    @property
    def completion_percent(self) -> int:
        fields = [self.business_name, self.industry, self.city, self.phone, self.description]
        return round(sum(bool(value) for value in fields) / len(fields) * 100)


class RoadmapStage(models.Model):
    key = models.SlugField(unique=True)
    order = models.PositiveIntegerField(unique=True)
    name = models.CharField(max_length=80)
    definition = models.TextField()
    xp_required = models.PositiveIntegerField(default=0)
    is_future = models.BooleanField(default=False)

    class Meta:
        ordering = ["order"]

    def __str__(self) -> str:
        return self.name


class ChecklistItem(models.Model):
    REQUIREMENT_TYPES = [
        ("manual_checklist", "Manual checklist"),
        ("file_evidence", "File evidence"),
        ("website_status", "Website status"),
        ("accounting_fact", "Accounting fact"),
        ("profile_field", "Profile field"),
        ("ai_review", "AI review"),
        ("admin_verification", "Admin verification"),
    ]
    key = models.SlugField(unique=True)
    stage = models.ForeignKey(RoadmapStage, related_name="checklist_items", on_delete=models.CASCADE)
    title = models.CharField(max_length=180)
    category = models.CharField(max_length=80)
    requirement_type = models.CharField(max_length=40, choices=REQUIREMENT_TYPES)
    xp_reward = models.PositiveIntegerField(default=10)
    score_dimension = models.CharField(max_length=80, blank=True)
    is_premium = models.BooleanField(default=False)

    class Meta:
        ordering = ["stage__order", "id"]

    def __str__(self) -> str:
        return self.title


class ChecklistCompletion(TenantModel):
    item = models.ForeignKey(ChecklistItem, related_name="completions", on_delete=models.CASCADE)
    status = models.CharField(max_length=20, default="completed")
    evidence_file_id = models.CharField(max_length=120, blank=True)
    note = models.TextField(blank=True)
    completed_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = [("organization_id", "tenant_id", "item")]


class VaultDocument(TenantModel):
    DOCUMENT_TYPES = [
        ("nib", "NIB"),
        ("npwp", "NPWP"),
        ("sop", "SOP"),
        ("template", "Template"),
        ("finance", "Finance"),
        ("legal", "Legal"),
        ("other", "Other"),
    ]
    title = models.CharField(max_length=180)
    document_type = models.CharField(max_length=40, choices=DOCUMENT_TYPES, default="other")
    file_id = models.CharField(max_length=120)
    source = models.CharField(max_length=80, default="file_manager")
    expires_at = models.DateField(null=True, blank=True)
    linked_checklist_item = models.ForeignKey(
        ChecklistItem, null=True, blank=True, on_delete=models.SET_NULL
    )


class XPTransaction(TenantModel):
    source_type = models.CharField(max_length=80)
    source_id = models.CharField(max_length=120)
    amount = models.PositiveIntegerField()
    reason = models.CharField(max_length=180)

    class Meta:
        unique_together = [("organization_id", "tenant_id", "source_type", "source_id")]


class ScoreSnapshot(TenantModel):
    version = models.PositiveIntegerField(default=1)
    overall_score = models.PositiveIntegerField(default=0)
    dimensions = models.JSONField(default=dict)
    explanation = models.JSONField(default=list)


class Goal(TenantModel):
    title = models.CharField(max_length=180)
    metric = models.CharField(max_length=80, blank=True)
    target_value = models.CharField(max_length=80, blank=True)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=30, default="active")


class CalendarEvent(TenantModel):
    title = models.CharField(max_length=180)
    event_type = models.CharField(max_length=60, default="reminder")
    starts_at = models.DateTimeField()
    reminder_enabled = models.BooleanField(default=False)
    notification_intent_id = models.CharField(max_length=120, blank=True)


class Achievement(TenantModel):
    key = models.SlugField()
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    unlocked_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = [("organization_id", "tenant_id", "key")]


class AIInsight(TenantModel):
    title = models.CharField(max_length=180)
    recommendation = models.TextField()
    related_action = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=30, default="generated")
    feedback = models.CharField(max_length=30, blank=True)


class IntegrationStatus(TenantModel):
    service = models.CharField(max_length=60)
    status = models.CharField(max_length=30, default="unknown")
    last_checked_at = models.DateTimeField(default=timezone.now)
    details = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = [("organization_id", "tenant_id", "service")]
