BUSINESS_HUB_PREFIX = "/api/v1/business-hub/"
TENANT_ID_PARAMETER = {
    "name": "tenant_id",
    "in": "query",
    "required": True,
    "description": "Tenant identifier for scoping the Business Hub request.",
    "schema": {
        "type": "string",
        "example": "tenant_demo",
    },
}


def add_tenant_id_query_parameter(result, generator, request, public):
    for path, path_item in result.get("paths", {}).items():
        if not path.startswith(BUSINESS_HUB_PREFIX):
            continue

        for operation in path_item.values():
            if not isinstance(operation, dict):
                continue

            parameters = operation.setdefault("parameters", [])
            has_tenant_id = any(
                parameter.get("name") == "tenant_id" and parameter.get("in") == "query"
                for parameter in parameters
            )
            if not has_tenant_id:
                parameters.insert(0, TENANT_ID_PARAMETER.copy())

    return result
