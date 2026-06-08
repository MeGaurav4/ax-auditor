import asyncio
import httpx
from .models import AuditReport, CheckResult
from .checks.mcp import check_mcp_support
from .checks.api_docs import check_api_docs
from .checks.headers import check_headers
from .checks.errors import check_error_clarity
from .checks.auth import check_auth_flow
from .checks.crawlability import check_crawlability


async def run_audit(url: str, timeout: int = 30) -> AuditReport:
    base_url = url.rstrip("/")

    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        checks = await asyncio.gather(
            check_mcp_support(client, base_url),
            check_api_docs(client, base_url),
            check_headers(client, base_url),
            check_error_clarity(client, base_url),
            check_auth_flow(client, base_url),
            check_crawlability(client, base_url),
            return_exceptions=True,
        )

    results: list[CheckResult] = []
    for c in checks:
        if isinstance(c, CheckResult):
            results.append(c)

    total_weight = sum(r.weight for r in results)
    if total_weight > 0:
        ax_score = sum(r.score * r.weight for r in results) / total_weight * 100
    else:
        ax_score = 0.0

    return AuditReport(
        url=base_url,
        ax_score=round(ax_score, 1),
        checks=results,
        summary=_generate_summary(results, ax_score),
    )


def _generate_summary(checks: list[CheckResult], ax_score: float) -> str:
    passed = sum(1 for c in checks if c.passed)
    total = len(checks)

    if ax_score >= 80:
        verdict = "Excellent"
    elif ax_score >= 60:
        verdict = "Good"
    elif ax_score >= 40:
        verdict = "Fair"
    else:
        verdict = "Poor"

    top_recs = []
    for c in checks:
        if not c.passed and c.recommendation:
            top_recs.append(f"- **{c.name}**: {c.recommendation}")
        elif c.score < 0.5 and c.recommendation:
            top_recs.append(f"- **{c.name}**: {c.recommendation}")

    recs_section = "\n".join(top_recs[:5]) if top_recs else "- No critical improvements needed"
    if len(top_recs) > 5:
        recs_section += f"\n- *...and {len(top_recs) - 5} more recommendations*"

    return f"""**AX Score: {ax_score}/100 — {verdict}**

Passed {passed}/{total} checks.

**Top Recommendations:**
{recs_section}"""


def audit(target: str, timeout: int = 30) -> AuditReport:
    return asyncio.run(run_audit(target, timeout))
