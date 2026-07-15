from django.contrib import admin

from .models import (
    AIInsight,
    Achievement,
    BusinessProfile,
    CalendarEvent,
    ChecklistCompletion,
    ChecklistItem,
    Goal,
    HubAsset,
    HubSettings,
    IntegrationStatus,
    RoadmapStage,
    ScoreSnapshot,
    VaultDocument,
    XPTransaction,
)


@admin.register(RoadmapStage)
class RoadmapStageAdmin(admin.ModelAdmin):
    list_display = ("order", "name", "key", "xp_required", "is_future")
    ordering = ("order",)


@admin.register(ChecklistItem)
class ChecklistItemAdmin(admin.ModelAdmin):
    list_display = ("title", "stage", "category", "requirement_type", "xp_reward", "is_premium")
    list_filter = ("stage", "category", "requirement_type", "is_premium")


for model in [
    BusinessProfile,
    ChecklistCompletion,
    VaultDocument,
    HubAsset,
    HubSettings,
    XPTransaction,
    ScoreSnapshot,
    Goal,
    CalendarEvent,
    Achievement,
    AIInsight,
    IntegrationStatus,
]:
    admin.site.register(model)
