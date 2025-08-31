from agents.task_decomposer import TaskDecomposerAgent

SAMPLE = """
id: demo
name: Demo
components:
  api:
    lang: python
  db:
    kind: sqlite
stages:
  deploy: false
component_order: ["api","db"]
"""


def test_decompose_sample_plan_yaml():
    agent = TaskDecomposerAgent()
    g = agent.decompose(SAMPLE)
    g.validate_acyclic()
    h1 = g.stable_hash()
    h2 = agent.decompose(SAMPLE).stable_hash()
    assert h1 == h2
