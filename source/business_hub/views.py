from django.db.models import Exists, OuterRef
from django.http import JsonResponse
from django.utils import timezone
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework import serializers
from rest_framework.response import Response

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
from .serializers import (
    AIInsightSerializer,
    AchievementSerializer,
    BusinessProfileSerializer,
    CalendarEventSerializer,
    ChecklistCompletionSerializer,
    ChecklistItemSerializer,
    GoalSerializer,
    IntegrationStatusSerializer,
    RoadmapStageSerializer,
    ScoreSnapshotSerializer,
    VaultDocumentSerializer,
    XPTransactionSerializer,
)
from .services import calculate_level, complete_checklist_item, recalculate_score, stamp_create, tenant_kwargs, xp_sum


@extend_schema(
    responses=inline_serializer(
        name="HealthLiveResponse",
        fields={
            "status": serializers.CharField(),
            "service": serializers.CharField(),
        },
    )
)
@api_view(["GET"])
def live(_request):
    return Response({"status": "ok", "service": "arna-business-hub"})


@extend_schema(
    responses=inline_serializer(
        name="HealthReadyResponse",
        fields={
            "status": serializers.CharField(),
            "checks": serializers.DictField(child=serializers.CharField()),
        },
    )
)
@api_view(["GET"])
def ready(_request):
    return Response({"status": "ready", "checks": {"database": "ok"}})


def forbidden(message: str = "Missing permission."):
    return Response({"detail": message}, status=status.HTTP_403_FORBIDDEN)


class TenantScopedViewSet(viewsets.ModelViewSet):
    def tenant_filter(self):
        return tenant_kwargs(self.request.business_context)

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False) or not hasattr(self.request, "business_context"):
            return self.queryset.none()
        return self.queryset.filter(**self.tenant_filter())

    def perform_create(self, serializer):
        stamp_create(serializer, self.request.business_context)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.business_context.user_id)


class BusinessProfileViewSet(TenantScopedViewSet):
    queryset = BusinessProfile.objects.all()
    serializer_class = BusinessProfileSerializer

    def get_queryset(self):
        return super().get_queryset().order_by("-updated_at")

    def perform_create(self, serializer):
        instance = serializer.save(
            organization_id=self.request.business_context.organization_id,
            tenant_id=self.request.business_context.tenant_id,
            created_by=self.request.business_context.user_id,
            updated_by=self.request.business_context.user_id,
        )
        if instance.completion_percent >= 80 and not instance.completed_at:
            instance.completed_at = timezone.now()
            instance.save(update_fields=["completed_at"])


class RoadmapStageViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RoadmapStageSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False) or not hasattr(self.request, "business_context"):
            return RoadmapStage.objects.prefetch_related("checklist_items").all()
        context = self.request.business_context
        completions = ChecklistCompletion.objects.filter(
            organization_id=context.organization_id,
            tenant_id=context.tenant_id,
            item=OuterRef("pk"),
        )
        return RoadmapStage.objects.prefetch_related("checklist_items").all().annotate()

    @extend_schema(responses=ChecklistItemSerializer(many=True))
    @action(detail=False, methods=["get"])
    def flat_checklist(self, request):
        context = request.business_context
        completions = ChecklistCompletion.objects.filter(
            organization_id=context.organization_id,
            tenant_id=context.tenant_id,
            item=OuterRef("pk"),
        )
        queryset = ChecklistItem.objects.select_related("stage").annotate(completed=Exists(completions))
        return Response(ChecklistItemSerializer(queryset, many=True).data)


class ChecklistCompletionViewSet(TenantScopedViewSet):
    queryset = ChecklistCompletion.objects.select_related("item")
    serializer_class = ChecklistCompletionSerializer

    def create(self, request, *args, **kwargs):
        item_id = request.data.get("item")
        if not item_id:
            return Response({"detail": "item is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            item = ChecklistItem.objects.get(id=item_id)
        except ChecklistItem.DoesNotExist:
            return Response({"detail": "Checklist item not found."}, status=status.HTTP_404_NOT_FOUND)
        if item.is_premium and request.business_context.plan == "free":
            return forbidden("Premium entitlement is required for this checklist item.")
        completion = complete_checklist_item(
            request.business_context,
            item,
            evidence_file_id=request.data.get("evidence_file_id", ""),
            note=request.data.get("note", ""),
        )
        return Response(self.get_serializer(completion).data, status=status.HTTP_201_CREATED)


class VaultDocumentViewSet(TenantScopedViewSet):
    queryset = VaultDocument.objects.all()
    serializer_class = VaultDocumentSerializer

    def create(self, request, *args, **kwargs):
        limit = 5 if request.business_context.plan == "free" else None
        if limit and self.get_queryset().count() >= limit:
            return forbidden("Free vault limit reached. Existing documents remain readable.")
        return super().create(request, *args, **kwargs)


class ScoreSnapshotViewSet(TenantScopedViewSet):
    queryset = ScoreSnapshot.objects.all()
    serializer_class = ScoreSnapshotSerializer

    def get_queryset(self):
        return super().get_queryset().order_by("-created_at")

    @action(detail=False, methods=["post"])
    def recalculate(self, request):
        snapshot = recalculate_score(request.business_context)
        return Response(self.get_serializer(snapshot).data, status=status.HTTP_201_CREATED)


class GoalViewSet(TenantScopedViewSet):
    queryset = Goal.objects.all()
    serializer_class = GoalSerializer


class CalendarEventViewSet(TenantScopedViewSet):
    queryset = CalendarEvent.objects.all()
    serializer_class = CalendarEventSerializer


class AchievementViewSet(TenantScopedViewSet):
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer
    http_method_names = ["get", "head", "options"]


class AIInsightViewSet(TenantScopedViewSet):
    queryset = AIInsight.objects.all()
    serializer_class = AIInsightSerializer

    def create(self, request, *args, **kwargs):
        if request.business_context.plan == "free":
            existing = self.get_queryset().count()
            if existing >= 1:
                return forbidden("Free AI insight quota reached.")
        title = request.data.get("title") or "Rekomendasi bisnis berikutnya"
        recommendation = request.data.get("recommendation") or (
            "Lengkapi profil bisnis, unggah dokumen legal utama, dan hubungkan data keuangan "
            "agar skor kesiapan dapat dihitung lebih akurat."
        )
        insight = AIInsight.objects.create(
            **self.tenant_filter(),
            created_by=request.business_context.user_id,
            updated_by=request.business_context.user_id,
            title=title,
            recommendation=recommendation,
            related_action=request.data.get("related_action", "complete-checklist"),
        )
        return Response(self.get_serializer(insight).data, status=status.HTTP_201_CREATED)


class IntegrationStatusViewSet(TenantScopedViewSet):
    queryset = IntegrationStatus.objects.all()
    serializer_class = IntegrationStatusSerializer


class XPTransactionViewSet(TenantScopedViewSet):
    queryset = XPTransaction.objects.all()
    serializer_class = XPTransactionSerializer
    http_method_names = ["get", "head", "options"]


@extend_schema(
    responses=inline_serializer(
        name="BusinessHubOverview",
        fields={
            "profile": BusinessProfileSerializer(allow_null=True),
            "level": serializers.DictField(),
            "score": ScoreSnapshotSerializer(allow_null=True),
            "today_quests": ChecklistItemSerializer(many=True),
            "integrations": IntegrationStatusSerializer(many=True),
            "achievements": AchievementSerializer(many=True),
            "quick_actions": serializers.ListField(child=serializers.CharField()),
        },
    )
)
@api_view(["GET"])
def overview(request):
    context = request.business_context
    tenant = tenant_kwargs(context)
    total_xp = xp_sum(context)
    latest_score = ScoreSnapshot.objects.filter(**tenant).order_by("-created_at").first()
    completed_ids = ChecklistCompletion.objects.filter(**tenant).values_list("item_id", flat=True)
    quests = ChecklistItem.objects.exclude(id__in=completed_ids).select_related("stage")[:5]
    profile = BusinessProfile.objects.filter(**tenant).first()
    integrations = IntegrationStatus.objects.filter(**tenant).order_by("service")
    achievements = Achievement.objects.filter(**tenant).order_by("-unlocked_at")[:5]
    payload = {
        "profile": BusinessProfileSerializer(profile).data if profile else None,
        "level": calculate_level(total_xp),
        "score": ScoreSnapshotSerializer(latest_score).data if latest_score else None,
        "today_quests": ChecklistItemSerializer(quests, many=True).data,
        "integrations": IntegrationStatusSerializer(integrations, many=True).data,
        "achievements": AchievementSerializer(achievements, many=True).data,
        "quick_actions": [
            "upload_document",
            "complete_checklist",
            "create_goal",
            "open_accounting",
            "edit_website",
            "ask_ai",
        ],
    }
    return JsonResponse(payload)
