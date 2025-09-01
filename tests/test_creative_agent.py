from agents.creative_enhancement.agent import CreativeEnhancementAgent


def test_generate_suggestions_enabled():
    agent = CreativeEnhancementAgent(enabled=True)
    task = {"type": "generate_code", "name": "test_task"}
    suggestions = agent.generate_suggestions(task)
    assert len(suggestions) > 0
    assert "Use type hints for better code quality." in suggestions
    assert isinstance(suggestions, list)


def test_generate_suggestions_disabled():
    agent = CreativeEnhancementAgent(enabled=False)
    task = {"type": "test", "name": "test_task"}
    suggestions = agent.generate_suggestions(task)
    assert suggestions == []


def test_generate_suggestions_custom_task():
    agent = CreativeEnhancementAgent()
    task = {"type": "custom", "name": "test_task"}
    suggestions = agent.generate_suggestions(task)
    assert len(suggestions) == 5  # Base suggestions
    assert "Consider using a more efficient algorithm" in suggestions[0]


def test_enable_disable():
    agent = CreativeEnhancementAgent(enabled=False)
    assert not agent.enabled
    agent.enable()
    assert agent.enabled
    agent.disable()
    assert not agent.enabled


def test_generate_suggestions_test_task():
    agent = CreativeEnhancementAgent()
    task = {"type": "test", "name": "test_task"}
    suggestions = agent.generate_suggestions(task)
    assert "Increase test coverage with edge cases." in suggestions
