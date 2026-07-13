from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("profiles", views.BusinessProfileViewSet, basename="profile")
router.register("roadmap", views.RoadmapStageViewSet, basename="roadmap")
router.register("checklist/completions", views.ChecklistCompletionViewSet, basename="checklist-completion")
router.register("vault/documents", views.VaultDocumentViewSet, basename="vault-document")
router.register("score/snapshots", views.ScoreSnapshotViewSet, basename="score-snapshot")
router.register("goals", views.GoalViewSet, basename="goal")
router.register("calendar/events", views.CalendarEventViewSet, basename="calendar-event")
router.register("achievements", views.AchievementViewSet, basename="achievement")
router.register("ai/insights", views.AIInsightViewSet, basename="ai-insight")
router.register("integrations/status", views.IntegrationStatusViewSet, basename="integration-status")
router.register("xp/transactions", views.XPTransactionViewSet, basename="xp-transaction")

urlpatterns = [
    path("overview/", views.overview, name="overview"),
    path("", include(router.urls)),
]
