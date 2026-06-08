from dataclasses import dataclass, field
from typing import Optional


@dataclass
class CheckResult:
    name: str
    passed: bool
    score: float
    weight: float
    detail: str
    recommendation: str
    evidence: Optional[str] = None


@dataclass
class AuditReport:
    url: str
    ax_score: float
    checks: list[CheckResult] = field(default_factory=list)
    summary: str = ""
