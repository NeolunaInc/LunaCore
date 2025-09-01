from services.agent_registry.signing import AgentRegistry, AgentSigner


def test_agent_signer_sign_and_verify():
    signer = AgentSigner("secret_key")
    agent_data = {"name": "test_agent", "version": "1.0", "type": "custom"}

    signature = signer.sign_agent(agent_data)
    assert signer.verify_agent(agent_data, signature) is True


def test_agent_signer_verify_invalid():
    signer = AgentSigner("secret_key")
    agent_data = {"name": "test_agent", "version": "1.0"}
    invalid_signature = "invalid_signature"

    assert signer.verify_agent(agent_data, invalid_signature) is False


def test_agent_signer_different_key():
    signer1 = AgentSigner("key1")
    signer2 = AgentSigner("key2")
    agent_data = {"name": "test_agent"}

    signature = signer1.sign_agent(agent_data)
    assert signer2.verify_agent(agent_data, signature) is False


def test_agent_registry_register_and_get():
    signer = AgentSigner("secret_key")
    registry = AgentRegistry(signer)

    agent_data = {"name": "test_agent", "type": "custom"}
    registry.register_agent("agent1", agent_data)

    retrieved = registry.get_agent("agent1")
    assert retrieved is not None
    assert retrieved["name"] == "test_agent"


def test_agent_registry_get_nonexistent():
    signer = AgentSigner("secret_key")
    registry = AgentRegistry(signer)

    retrieved = registry.get_agent("nonexistent")
    assert retrieved is None


def test_agent_registry_invalid_signature():
    signer = AgentSigner("secret_key")
    registry = AgentRegistry(signer)

    # Manually tamper with stored data
    agent_data = {"name": "test_agent"}
    registry.register_agent("agent1", agent_data)
    # Tamper with stored data
    registry.agents["agent1"]["name"] = "tampered"

    try:
        registry.get_agent("agent1")
        raise AssertionError("Should have raised ValueError")
    except ValueError as e:
        assert "invalid signature" in str(e)


def test_canonicalize():
    signer = AgentSigner("key")
    data = {"b": 2, "a": 1, "c": {"x": 3, "y": 4}}
    canonical = signer._canonicalize(data)
    # Should be sorted: a:1|b:2|c:x:3|y:4
    expected = "a:1|b:2|c:x:3|y:4"
    assert canonical == expected
