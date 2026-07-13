from rest_framework import serializers

from .models import (
    AIInsight,
    Achievement,
    BusinessProfile,
    CalendarEvent,
    ChecklistCompletion,
    ChecklistItem,
    Goal,
    IntegrationStatus,
    RoadmapStage,
    ScoreSnapshot,
    VaultDocument,
    XPTransaction,
)


class BusinessProfileSerializer(serializers.ModelSerializer):
    completion_percent = serializers.IntegerField(read_only=True)

    class Meta:
        model = BusinessProfile
        fields = [
            "id",
            "business_name",
            "industry",
            "business_stage",
            "city",
            "phone",
            "website_url",
            "description",
            "completion_percent",
            "completed_at",
            "created_at",
            "updated_at",
        ]


class ChecklistItemSerializer(serializers.ModelSerializer):
    stage_name = serializers.CharField(source="stage.name", read_only=True)
    completed = serializers.BooleanField(read_only=True)

    class Meta:
        model = ChecklistItem
        fields = [
            "id",
            "key",
            "stage",
            "stage_name",
            "title",
            "category",
            "requirement_type",
            "xp_reward",
            "score_dimension",
            "is_premium",
            "completed",
        ]


class RoadmapStageSerializer(serializers.ModelSerializer):
    checklist_items = ChecklistItemSerializer(many=True, read_only=True)

    class Meta:
        model = RoadmapStage
        fields = ["id", "key", "order", "name", "definition", "xp_required", "is_future", "checklist_items"]


class ChecklistCompletionSerializer(serializers.ModelSerializer):
    item_title = serializers.CharField(source="item.title", read_only=True)

    class Meta:
        model = ChecklistCompletion
        fields = ["id", "item", "item_title", "status", "evidence_file_id", "note", "completed_at"]
        read_only_fields = ["status", "completed_at"]


class VaultDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = VaultDocument
        fields = [
            "id",
            "title",
            "document_type",
            "file_id",
            "source",
            "expires_at",
            "linked_checklist_item",
            "created_at",
            "updated_at",
        ]


class XPTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = XPTransaction
        fields = ["id", "source_type", "source_id", "amount", "reason", "created_at"]


class ScoreSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScoreSnapshot
        fields = ["id", "version", "overall_score", "dimensions", "explanation", "created_at"]


class GoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = ["id", "title", "metric", "target_value", "due_date", "status", "created_at", "updated_at"]


class CalendarEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalendarEvent
        fields = [
            "id",
            "title",
            "event_type",
            "starts_at",
            "reminder_enabled",
            "notification_intent_id",
            "created_at",
            "updated_at",
        ]


class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = ["id", "key", "title", "description", "unlocked_at"]


class AIInsightSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIInsight
        fields = ["id", "title", "recommendation", "related_action", "status", "feedback", "created_at"]


class IntegrationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntegrationStatus
        fields = ["id", "service", "status", "last_checked_at", "details"]
