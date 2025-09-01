from services.metrics.kpis import (
    calculate_average_response_time,
    calculate_completion_rate,
    calculate_escalation_rate,
    check_slo_compliance,
)


def test_calculate_completion_rate():
    projects = [{"status": "completed"}, {"status": "in_progress"}, {"status": "completed"}]
    rate = calculate_completion_rate(projects)
    assert rate == 2 / 3


def test_calculate_completion_rate_empty():
    rate = calculate_completion_rate([])
    assert rate == 0.0


def test_calculate_escalation_rate():
    executions = [{"escalated": True}, {"escalated": False}, {"escalated": True}]
    rate = calculate_escalation_rate(executions)
    assert rate == 2 / 3


def test_calculate_escalation_rate_empty():
    rate = calculate_escalation_rate([])
    assert rate == 0.0


def test_calculate_average_response_time():
    executions = [{"response_time": 10.0}, {"response_time": 20.0}, {"response_time": 30.0}]
    avg = calculate_average_response_time(executions)
    assert avg == 20.0


def test_calculate_average_response_time_no_times():
    executions = [{"status": "completed"}]
    avg = calculate_average_response_time(executions)
    assert avg == 0.0


def test_check_slo_compliance():
    compliance = check_slo_compliance(0.96, 0.03, 25.0)
    assert compliance["completion_slo"] is True
    assert compliance["escalation_slo"] is True
    assert compliance["response_time_slo"] is True


def test_check_slo_compliance_failure():
    compliance = check_slo_compliance(0.90, 0.10, 35.0)
    assert compliance["completion_slo"] is False
    assert compliance["escalation_slo"] is False
    assert compliance["response_time_slo"] is False
