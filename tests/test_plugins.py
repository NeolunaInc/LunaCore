import os
import tempfile

import yaml

from services.agent_registry.plugins import discover_plugins


def test_discover_plugins():
    # Create a temporary directory structure
    with tempfile.TemporaryDirectory() as temp_dir:
        plugins_dir = os.path.join(temp_dir, "plugins")
        os.makedirs(plugins_dir)

        # Create example plugin
        plugin_dir = os.path.join(plugins_dir, "test_plugin")
        os.makedirs(plugin_dir)
        plugin_yaml = os.path.join(plugin_dir, "plugin.yaml")
        config = {
            "name": "Test Plugin",
            "version": "1.0.0",
            "description": "Test plugin",
            "agents": [{"name": "test_agent"}],
        }
        with open(plugin_yaml, "w") as f:
            yaml.dump(config, f)

        # Discover plugins
        plugins = discover_plugins(plugins_dir)
        assert len(plugins) == 1
        assert plugins[0]["name"] == "Test Plugin"
        assert plugins[0]["path"] == plugin_dir


def test_discover_plugins_no_dir():
    plugins = discover_plugins("nonexistent")
    assert plugins == []


def test_discover_plugins_invalid_yaml():
    with tempfile.TemporaryDirectory() as temp_dir:
        plugins_dir = os.path.join(temp_dir, "plugins")
        os.makedirs(plugins_dir)
        plugin_dir = os.path.join(plugins_dir, "bad_plugin")
        os.makedirs(plugin_dir)
        plugin_yaml = os.path.join(plugin_dir, "plugin.yaml")
        with open(plugin_yaml, "w") as f:
            f.write("invalid: yaml: content: [\n")

        plugins = discover_plugins(plugins_dir)
        # Should handle error gracefully, perhaps empty or with error
        assert len(plugins) == 0  # Assuming error skips the plugin
