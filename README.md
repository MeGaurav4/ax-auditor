# AX Auditor 🔍

**Agent Experience Auditor** — CLI tool that audits how "agent-friendly" any web service is. Checks MCP support, API documentation quality, error clarity, auth flow, crawlability, and HTTP headers.

> "You optimized for UX. Now optimize for aGENT eXPERIENCE."

## Why

AI agents (Claude, GPT, Gemini, Perplexity) are becoming the primary interface for users to interact with software. But most SaaS products weren't designed for agents — they're designed for human eyeballs. AX Auditor diagnoses the gap.

## Install

```bash
git clone https://github.com/MeGaurav4/ax-auditor
cd ax-auditor
pip install -e .
```

## Usage

```bash
# Console output
ax-auditor https://your-service.com

# Markdown report
ax-auditor https://your-service.com --format markdown --output report.md
```

## Checks

| Check | Weight | What it measures |
|-------|--------|-----------------|
| MCP Server Support | 20% | Is there an MCP server? |
| API Documentation Quality | 20% | OpenAPI spec? Clear docs? |
| HTTP Headers | 15% | Rate limits, CORS, content-type |
| Error Response Clarity | 15% | Structured error messages? |
| Authentication Flow | 15% | API-key friendly? |
| AI Crawlability | 15% | robots.txt for AI crawlers? |

## License

MIT

Built by [Gaurav Yadav](https://github.com/MeGaurav4)
