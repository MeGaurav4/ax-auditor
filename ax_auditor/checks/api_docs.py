import httpx
from ..models import CheckResult


async def check_api_docs(client: httpx.AsyncClient, base_url: str) -> CheckResult:
    score = 0.0
    findings = []
    recs = []

    doc_paths = [
        "/docs",
        "/api/docs",
        "/documentation",
        "/api-docs",
        "/api/v1/docs",
        "/reference",
        "/docs/api",
        "/developer",
        "/swagger.json",
        "/openapi.json",
    ]

    found_docs = False
    found_openapi = False
    for path in doc_paths:
        try:
            resp = await client.get(f"{base_url.rstrip('/')}{path}", timeout=10, follow_redirects=True)
            if resp.status_code == 200:
                ct = resp.headers.get("content-type", "")
                if "json" in ct and path.endswith((".json",)):
                    if "openapi" in resp.text.lower() or "swagger" in resp.text.lower():
                        found_openapi = True
                        findings.append(f"OpenAPI/Swagger spec at {path}")
                else:
                    found_docs = True
                    if not found_openapi:
                        findings.append(f"Documentation page at {path}")
        except httpx.RequestError:
            continue

    if found_openapi:
        score = 1.0
        findings.append("Structured API spec available (ideal for AI agents)")
        recs.append("Keep the OpenAPI spec up to date with all endpoints")
    elif found_docs:
        score = 0.7
        findings.append("Documentation found but no structured OpenAPI spec")
        recs.append("Add an OpenAPI/Swagger spec for better AI agent integration")
    else:
        score = 0.0
        findings.append("No API documentation found at standard paths")
        recs.append("Create public API documentation with an OpenAPI specification")

    return CheckResult(
        name="API Documentation Quality",
        passed=found_docs or found_openapi,
        score=score,
        weight=0.20,
        detail=" | ".join(findings),
        recommendation=" ".join(recs),
    )
