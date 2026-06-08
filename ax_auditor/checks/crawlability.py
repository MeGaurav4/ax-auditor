import httpx
from ..models import CheckResult


async def check_crawlability(client: httpx.AsyncClient, base_url: str) -> CheckResult:
    score = 0.0
    findings = []
    recs = []

    try:
        resp = await client.get(f"{base_url.rstrip('/')}/robots.txt", timeout=10)
        if resp.status_code == 200:
            body = resp.text.lower()
            findings.append("robots.txt found")

            agent_names = ["gptbot", "claudebot", "perplexitybot", "google-extended", "ccbot"]
            allowed_agents = []
            disallowed_agents = []

            lines = body.split("\n")
            current_agent = None
            for line in lines:
                line = line.strip()
                if line.startswith("user-agent:"):
                    agent = line.split(":", 1)[1].strip().lower()
                    current_agent = agent if agent != "*" else "wildcard"
                elif line.startswith("disallow:") and current_agent:
                    path = line.split(":", 1)[1].strip()
                    if path != "/":
                        disallowed_agents.append(f"{current_agent}: {path}")
                elif line.startswith("allow:") and current_agent:
                    allowed_agents.append(f"{current_agent}: {line.split(':', 1)[1].strip()}")

            for name in agent_names:
                if any(name in a for a in allowed_agents):
                    findings.append(f"Explicitly allows {name}")
                elif any(name in a for a in disallowed_agents):
                    findings.append(f"Explicitly disallows {name}")
                    score -= 0.1

            if disallowed_agents:
                recs.append("Review disallowed paths for AI crawlers — may block agent access")
            else:
                score += 0.3

            if any("sitemap" in line for line in lines):
                findings.append("Sitemap referenced in robots.txt")
                score += 0.2

        else:
            findings.append("No robots.txt found")
            recs.append("Add robots.txt with AI crawler permissions")
    except httpx.RequestError:
        findings.append("Could not fetch robots.txt")
        recs.append("Ensure robots.txt is publicly accessible")

    score = max(0.0, min(score + 0.5, 1.0))
    passed = score >= 0.5

    return CheckResult(
        name="AI Crawlability",
        passed=passed,
        score=score,
        weight=0.15,
        detail=" | ".join(findings),
        recommendation=" ".join(recs),
    )
