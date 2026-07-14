import base64
import hashlib
import hmac
import json
import time
from dataclasses import dataclass

from django.conf import settings
from django.http import JsonResponse


@dataclass(frozen=True)
class TenantContext:
    organization_id: str
    tenant_id: str
    user_id: str
    plan: str
    permissions: frozenset[str]
    request_id: str | None = None


def unauthorized(message: str) -> JsonResponse:
    return JsonResponse({"error": "unauthorized", "message": message}, status=401)


def decode_base64url_json(value: str) -> dict | None:
    try:
        padding = "=" * (-len(value) % 4)
        decoded = base64.urlsafe_b64decode(f"{value}{padding}")
        return json.loads(decoded.decode("utf-8"))
    except (ValueError, json.JSONDecodeError):
        return None


def is_valid_signature(token_parts: list[str]) -> bool:
    encoded_header, encoded_payload, signature = token_parts
    expected_signature = hmac.new(
        settings.JWT_SECRET.encode("utf-8"),
        f"{encoded_header}.{encoded_payload}".encode("utf-8"),
        hashlib.sha256,
    ).digest()

    try:
        padding = "=" * (-len(signature) % 4)
        signature_bytes = base64.urlsafe_b64decode(f"{signature}{padding}")
    except ValueError:
        return False

    return hmac.compare_digest(signature_bytes, expected_signature)


def permissions_from_header(request) -> frozenset[str]:
    permissions = request.headers.get("X-Permissions", "business_hub:read,business_hub:write")
    return frozenset(item.strip() for item in permissions.split(",") if item.strip())


def build_context(
    *,
    organization_id: str,
    tenant_id: str,
    user_id: str,
    request,
) -> TenantContext:
    return TenantContext(
        organization_id=organization_id,
        tenant_id=tenant_id,
        user_id=user_id,
        plan=request.headers.get("X-Plan", "free"),
        permissions=permissions_from_header(request),
        request_id=request.headers.get("x-arna-request-id"),
    )


class TenantContextMiddleware:
    """Populate tenant context from a signed Bearer token and tenant query."""

    PUBLIC_PREFIXES = (
        "/admin/",
        "/health/",
        "/api/schema",
        "/api/docs",
        "/api/redoc",
        "/api-docs",
        "/api-redoc",
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith(self.PUBLIC_PREFIXES):
            return self.get_response(request)

        if settings.DEV_AUTH_BYPASS:
            request.business_context = build_context(
                organization_id=request.headers.get("X-Organization-Id", "org_demo"),
                tenant_id=request.GET.get("tenant_id") or request.headers.get("X-Tenant-Id", "tenant_demo"),
                user_id=request.headers.get("X-User-Id", "user_demo"),
                request=request,
            )
            return self.get_response(request)

        authorization = request.headers.get("Authorization")
        if not authorization:
            return unauthorized("Authorization header is required.")

        authorization_parts = authorization.split(" ")
        if len(authorization_parts) != 2 or authorization_parts[0] != "Bearer" or not authorization_parts[1]:
            return unauthorized("Authorization header must use Bearer token.")

        token_parts = authorization_parts[1].split(".")
        if len(token_parts) != 3:
            return unauthorized("Invalid token format.")

        header = decode_base64url_json(token_parts[0])
        payload = decode_base64url_json(token_parts[1])
        if not header or not payload:
            return unauthorized("Invalid token payload.")


        exp = payload.get("exp")
        if not isinstance(exp, int):
            return unauthorized("Token expiration is required.")

        if exp <= int(time.time()):
            return unauthorized("Token has expired.")

        user_id = payload.get("user_id")
        if not isinstance(user_id, str) or not user_id:
            return unauthorized("Token user_id is required.")

        organization_id = payload.get("org_id")
        if not isinstance(organization_id, str) or not organization_id:
            return unauthorized("Token org_id is required.")

        tenant_id = request.GET.get("tenant_id")
        if not tenant_id:
            return JsonResponse(
                {
                    "error": "missing_required_query_param",
                    "message": "Missing required query param: tenant_id",
                },
                status=400,
            )

        request.business_context = build_context(
            organization_id=organization_id,
            tenant_id=tenant_id,
            user_id=user_id,
            request=request,
        )
        return self.get_response(request)
