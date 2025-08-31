from core.task_graph import Task, TaskGraph


def test_cycle_detection():
    a = Task(name="A", type="custom", depends_on=[])
    b = Task(name="B", type="custom", depends_on=[a.compute_id("p")])
    # cycle: make A depend on B
    a.depends_on.append(b.compute_id("p"))
    g = TaskGraph(plan_id="p", tasks=[a, b])
    try:
        g.validate_acyclic()
        raise AssertionError("Expected cycle detection to fail")
    except ValueError:
        pass


def test_topological_and_hash_stability():
    a = Task(name="A", type="custom", depends_on=[])
    b = Task(name="B", type="custom", depends_on=[a.compute_id("p")])
    g1 = TaskGraph(plan_id="p", tasks=[a, b])
    g2 = TaskGraph(plan_id="p", tasks=[a, b])
    g1.validate_acyclic()
    g2.validate_acyclic()
    assert g1.topological_order() == g2.topological_order()
    assert g1.stable_hash() == g2.stable_hash()


def test_export_json_deterministic():
    a = Task(name="A", type="custom", depends_on=[])
    b = Task(name="B", type="custom", depends_on=[a.compute_id("p")])
    g = TaskGraph(plan_id="p", tasks=[a, b])
    j1 = g.to_json()
    j2 = g.to_json()
    assert j1 == j2
