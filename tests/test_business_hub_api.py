import base64
import hashlib
import hmac
import json
import time

from django.core.management import call_command
from django.test import override_settings
from django.test import TestCase
from rest_framework.test import APIClient

from business_hub.models import ChecklistItem, XPTransaction


def base64url_json(value):
    encoded = base64.urlsafe_b64encode(json.dumps(value, separators=(",", ":")).encode("utf-8")).decode("ascii")
    return encoded.rstrip("=")


def make_token(secret, payload):
    header = base64url_json({"alg": "HS256", "typ": "JWT"})
    body = base64url_json(payload)
    signature = hmac.new(secret.encode("utf-8"), f"{header}.{body}".encode("utf-8"), hashlib.sha256).digest()
    encoded_signature = base64.urlsafe_b64encode(signature).decode("ascii").rstrip("=")
    return f"{header}.{body}.{encoded_signature}"


class BusinessHubCorsTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_local_preflight_returns_cors_headers_before_auth(self):
        response = self.client.options(
            "/api/v1/business-hub/overview/",
            HTTP_ORIGIN="http://localhost:3001",
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="GET",
            HTTP_ACCESS_CONTROL_REQUEST_HEADERS="authorization,content-type,baggage,sentry-trace,x-tenant-id",
            HTTP_ACCESS_CONTROL_REQUEST_PRIVATE_NETWORK="true",
        )

        self.assertEqual(response.status_code, 204)
        self.assertEqual(response["Access-Control-Allow-Origin"], "*")
        self.assertIn("authorization", response["Access-Control-Allow-Headers"])
        self.assertIn("baggage", response["Access-Control-Allow-Headers"])
        self.assertNotIn("Access-Control-Allow-Credentials", response)
        self.assertEqual(response["Access-Control-Allow-Private-Network"], "true")
        self.assertIn("GET", response["Access-Control-Allow-Methods"])


@override_settings(DEV_AUTH_BYPASS=True)
class BusinessHubDevAuthBypassTests(TestCase):
    def setUp(self):
        call_command("seed_business_hub", verbosity=0)
        self.client = APIClient()

    def test_local_dev_can_use_tenant_headers_without_authorization(self):
        response = self.client.get(
            "/api/v1/business-hub/overview/?tenant_id=tenant_test",
            HTTP_X_ORGANIZATION_ID="org_test",
            HTTP_X_USER_ID="user_test",
            HTTP_X_PLAN="free",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["level"]["level"], "Level 1")

    def test_local_dev_requires_tenant_id_query_param(self):
        response = self.client.get(
            "/api/v1/business-hub/overview/",
            HTTP_X_ORGANIZATION_ID="org_test",
            HTTP_X_USER_ID="user_test",
            HTTP_X_PLAN="free",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "missing_required_query_param")


class BusinessHubSchemaTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_business_hub_operations_include_required_tenant_id_query_param(self):
        response = self.client.get("/api/schema/?format=json")

        self.assertEqual(response.status_code, 200)
        overview_operation = response.json()["paths"]["/api/v1/business-hub/overview/"]["get"]
        tenant_parameter = next(
            parameter
            for parameter in overview_operation["parameters"]
            if parameter["name"] == "tenant_id" and parameter["in"] == "query"
        )
        self.assertTrue(tenant_parameter["required"])


@override_settings(JWT_SECRET="test-secret", DEV_AUTH_BYPASS=False)
class BusinessHubApiTests(TestCase):
    def setUp(self):
        call_command("seed_business_hub", verbosity=0)
        self.client = APIClient()
        token = make_token(
            "test-secret",
            {
                "exp": int(time.time()) + 3600,
                "user_id": "user_test",
                "org_id": "org_test",
            },
        )
        self.headers = {
            "HTTP_AUTHORIZATION": f"Bearer {token}",
            "HTTP_X_PLAN": "free",
        }
        self.tenant_query = "?tenant_id=tenant_test"

    def test_overview_returns_seeded_quests(self):
        response = self.client.get(f"/api/v1/business-hub/overview/{self.tenant_query}", **self.headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["level"]["level"], "Level 1")
        self.assertGreaterEqual(len(response.json()["today_quests"]), 1)

    def test_checklist_completion_awards_xp_once(self):
        item = ChecklistItem.objects.get(key="complete-profile")

        first = self.client.post(
            f"/api/v1/business-hub/checklist/completions/{self.tenant_query}",
            {"item": item.id, "note": "Done"},
            format="json",
            **self.headers,
        )
        second = self.client.post(
            f"/api/v1/business-hub/checklist/completions/{self.tenant_query}",
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
                f"/api/v1/business-hub/vault/documents/{self.tenant_query}",
                {"title": f"Doc {index}", "document_type": "other", "file_id": f"file_{index}"},
                format="json",
                **self.headers,
            )
            self.assertEqual(response.status_code, 201)

        blocked = self.client.post(
            f"/api/v1/business-hub/vault/documents/{self.tenant_query}",
            {"title": "Doc 6", "document_type": "other", "file_id": "file_6"},
            format="json",
            **self.headers,
        )

        self.assertEqual(blocked.status_code, 403)

    def test_score_recalculate_uses_current_facts(self):
        self.client.post(
            f"/api/v1/business-hub/vault/documents/{self.tenant_query}",
            {"title": "NIB", "document_type": "nib", "file_id": "file_nib"},
            format="json",
            **self.headers,
        )

        response = self.client.post(
            f"/api/v1/business-hub/score/snapshots/recalculate/{self.tenant_query}",
            {},
            format="json",
            **self.headers,
        )

        self.assertEqual(response.status_code, 201)
        self.assertGreaterEqual(response.json()["overall_score"], 25)
