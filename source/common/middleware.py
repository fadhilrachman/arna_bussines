from django.conf import settings
from django.http import HttpResponse


class CorsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if self.is_preflight(request) and self.is_allowed_origin(request):
            response = HttpResponse(status=204)
        else:
            response = self.get_response(request)

        origin = request.headers.get("Origin")
        if origin and self.is_allowed_origin(request):
            response["Access-Control-Allow-Origin"] = origin
            response["Vary"] = self.append_vary(response.get("Vary"), "Origin")
            response["Access-Control-Allow-Methods"] = ", ".join(settings.CORS_ALLOW_METHODS)
            response["Access-Control-Allow-Headers"] = self.allow_headers(request)
            if settings.CORS_ALLOW_CREDENTIALS:
                response["Access-Control-Allow-Credentials"] = "true"
            if settings.CORS_PREFLIGHT_MAX_AGE:
                response["Access-Control-Max-Age"] = str(settings.CORS_PREFLIGHT_MAX_AGE)

        return response

    def is_preflight(self, request) -> bool:
        return request.method == "OPTIONS" and bool(request.headers.get("Access-Control-Request-Method"))

    def is_allowed_origin(self, request) -> bool:
        if settings.CORS_ALLOW_ALL_ORIGINS and settings.ENVIRONMENT != "production":
            return True
        return request.headers.get("Origin") in settings.CORS_ALLOWED_ORIGINS

    def allow_headers(self, request) -> str:
        requested_headers = request.headers.get("Access-Control-Request-Headers")
        if requested_headers and settings.ENVIRONMENT != "production":
            return requested_headers
        return ", ".join(settings.CORS_ALLOW_HEADERS)

    def append_vary(self, current: str | None, value: str) -> str:
        if not current:
            return value

        values = [item.strip() for item in current.split(",")]
        if value not in values:
            values.append(value)
        return ", ".join(values)
