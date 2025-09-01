from typing import Any


def calculate_completion_rate(projects: list[dict[str, Any]]) -> float:
    """
    Calculate the project completion rate.
    """
    if not projects:
        return 0.0
    completed = sum(1 for p in projects if p.get("status") == "completed")
    return completed / len(projects)


def calculate_escalation_rate(executions: list[dict[str, Any]]) -> float:
    """
    Calculate the escalation rate to human intervention.
    """
    if not executions:
        return 0.0
    escalated = sum(1 for e in executions if e.get("escalated", False))
    return escalated / len(executions)


def calculate_average_response_time(executions: list[dict[str, Any]]) -> float:
    """
    Calculate the average response time for executions.
    """
    times = [e.get("response_time", 0) for e in executions if e.get("response_time")]
    if not times:
        return 0.0
    return sum(times) / len(times)


def check_slo_compliance(
    completion_rate: float, escalation_rate: float, avg_response_time: float
) -> dict[str, bool]:
    """
    Check if SLOs are met.
    Example SLOs: completion > 95%, escalation < 5%, response time < 30s
    """
    return {
        "completion_slo": completion_rate >= 0.95,
        "escalation_slo": escalation_rate <= 0.05,
        "response_time_slo": avg_response_time <= 30.0,
    }
