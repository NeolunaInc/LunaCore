from services.costing.tracker import CostTracker, track_openai_cost


def test_cost_tracker_add_cost():
    tracker = CostTracker()
    tracker.add_cost(10.0, "Test cost")
    assert tracker.get_total_cost() == 10.0
    assert len(tracker.costs) == 1


def test_cost_tracker_budget_alert():
    alert_triggered = False

    def alert_callback(cost):
        nonlocal alert_triggered
        alert_triggered = True

    tracker = CostTracker(budget_limit=100.0, alert_threshold=0.8)
    tracker.set_alert_callback(alert_callback)
    tracker.add_cost(80.0, "High cost")  # 80% of 100
    assert alert_triggered is True


def test_cost_tracker_no_alert():
    alert_triggered = False

    def alert_callback(cost):
        nonlocal alert_triggered
        alert_triggered = True

    tracker = CostTracker(budget_limit=100.0, alert_threshold=0.8)
    tracker.set_alert_callback(alert_callback)
    tracker.add_cost(70.0, "Lower cost")  # 70% of 100
    assert alert_triggered is False


def test_get_costs_by_type():
    tracker = CostTracker()
    tracker.add_cost(10.0, "API cost", {"type": "api"})
    tracker.add_cost(5.0, "Compute cost", {"type": "compute"})
    tracker.add_cost(15.0, "API cost 2", {"type": "api"})

    api_costs = tracker.get_costs_by_type("api")
    assert len(api_costs) == 2
    assert sum(c["amount"] for c in api_costs) == 25.0


def test_reset():
    tracker = CostTracker()
    tracker.add_cost(10.0, "Test cost")
    tracker.reset()
    assert tracker.get_total_cost() == 0.0
    assert len(tracker.costs) == 0


def test_track_openai_cost():
    tracker = CostTracker()
    track_openai_cost(tracker, 1000, "gpt-3.5-turbo")
    # 1000 tokens * 0.002 / 1000 = 0.002
    assert tracker.get_total_cost() == 0.002
    api_costs = tracker.get_costs_by_type("api")
    assert len(api_costs) == 1
    assert api_costs[0]["metadata"]["tokens"] == 1000
