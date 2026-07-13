from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from business_hub.models import ChecklistItem, XPTransaction


class BusinessHubApiTests(TestCase):
    def setUp(self):
        call_command("seed_business_hub", verbosity=0)
        self.client = APIClient()
        self.headers = {
            "HTTP_X_ORGANIZATION_ID": "org_test",
            "HTTP_X_TENANT_ID": "tenant_test",
            "HTTP_X_USER_ID": "user_test",
            "HTTP_X_PLAN": "free",
        }

    def test_overview_returns_seeded_quests(self):
        response = self.client.get("/api/v1/business-hub/overview/", **self.headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["level"]["level"], "Level 1")
        self.assertGreaterEqual(len(response.json()["today_quests"]), 1)

    def test_checklist_completion_awards_xp_once(self):
        item = ChecklistItem.objects.get(key="complete-profile")

        first = self.client.post(
            "/api/v1/business-hub/checklist/completions/",
            {"item": item.id, "note": "Done"},
            format="json",
            **self.headers,
        )
        second = self.client.post(
            "/api/v1/business-hub/checklist/completions/",
            {"item": item.id, "note": "Done again"},
            format="json",
            **self.headers,
        )

        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 201)
        self.assertEqual(XPTransaction.objects.count(), 1)

    def test_free_vault_limit_blocks_creation_after_five(self):
        for index in range(5):
            response = self.client.post(
                "/api/v1/business-hub/vault/documents/",
                {"title": f"Doc {index}", "document_type": "other", "file_id": f"file_{index}"},
                format="json",
                **self.headers,
            )
            self.assertEqual(response.status_code, 201)

        blocked = self.client.post(
            "/api/v1/business-hub/vault/documents/",
            {"title": "Doc 6", "document_type": "other", "file_id": "file_6"},
            format="json",
            **self.headers,
        )

        self.assertEqual(blocked.status_code, 403)

    def test_score_recalculate_uses_current_facts(self):
        self.client.post(
            "/api/v1/business-hub/vault/documents/",
            {"title": "NIB", "document_type": "nib", "file_id": "file_nib"},
            format="json",
            **self.headers,
        )

        response = self.client.post(
            "/api/v1/business-hub/score/snapshots/recalculate/",
            {},
            format="json",
            **self.headers,
        )

        self.assertEqual(response.status_code, 201)
        self.assertGreaterEqual(response.json()["overall_score"], 25)
