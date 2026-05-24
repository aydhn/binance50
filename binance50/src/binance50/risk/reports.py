from binance50.config.models import AppConfig
from binance50.risk.limits import build_limit_report
from binance50.risk.models import RiskAssessment, RiskRunResult


def build_risk_run_summary(result: RiskRunResult) -> dict:
    return {
        "success": result.success,
        "error": result.error,
        "assessments_count": len(result.assessments),
        "rejected_count": len(result.rejected_assessments),
        "quality_report": result.quality_report.model_dump() if result.quality_report else None,
        "metadata": result.metadata,
    }


def build_risk_assessment_table(assessments: list[RiskAssessment], limit: int = 50) -> list[dict]:
    return [a.model_dump() for a in assessments[:limit]]


def build_risk_component_report(assessment: RiskAssessment) -> dict:
    return assessment.breakdown.model_dump()


def build_risk_distribution_report(assessments: list[RiskAssessment]) -> dict:
    dist = {}
    for a in assessments:
        dist[a.status.value] = dist.get(a.status.value, 0) + 1
    return dist


def build_risk_health_report(config: AppConfig) -> dict:
    return {
        "config_enabled": config.risk.enabled,
        "execution_forbidden": config.risk.execution_forbidden,
        "order_creation_forbidden": config.risk.order_creation_forbidden,
        "limits": build_limit_report(config),
    }
