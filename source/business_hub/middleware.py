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


class TenantContextMiddleware:
    """Development tenant context shim.

    Production SSO validation should replace the header trust boundary while
    keeping request.business_context stable for views and services.
    """

    PUBLIC_PREFIXES = ("/admin/", "/health/", "/api/schema")

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith(self.PUBLIC_PREFIXES):
            return self.get_response(request)

        organization_id = request.headers.get("X-Organization-Id")
        tenant_id = request.headers.get("X-Tenant-Id")
        user_id = request.headers.get("X-User-Id")

        if settings.DEV_AUTH_BYPASS:
            organization_id = organization_id or "org_demo"
            tenant_id = tenant_id or "tenant_demo"
            user_id = user_id or "user_demo"

        if not all([organization_id, tenant_id, user_id]):
            return JsonResponse(
                {"detail": "Missing tenant context or authenticated SSO claims."},
                status=401,
            )

        permissions = request.headers.get("X-Permissions", "business_hub:read,business_hub:write")
        request.business_context = TenantContext(
            organization_id=organization_id,
            tenant_id=tenant_id,
            user_id=user_id,
            plan=request.headers.get("X-Plan", "free"),
            permissions=frozenset(item.strip() for item in permissions.split(",") if item.strip()),
        )
        return self.get_response(request)
