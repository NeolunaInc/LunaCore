import os
from typing import Any

import yaml


def discover_plugins(plugins_dir: str = "plugins") -> list[dict[str, Any]]:
    """
    Discover plugins by scanning the plugins directory for plugin.yaml files.
    """
    plugins = []
    if not os.path.exists(plugins_dir):
        return plugins

    for item in os.listdir(plugins_dir):
        plugin_path = os.path.join(plugins_dir, item)
        if os.path.isdir(plugin_path):
            yaml_file = os.path.join(plugin_path, "plugin.yaml")
            if os.path.exists(yaml_file):
                try:
                    with open(yaml_file) as f:
                        plugin_config = yaml.safe_load(f)
                        plugin_config["path"] = plugin_path
                        plugins.append(plugin_config)
                except yaml.YAMLError as e:
                    print(f"Error loading {yaml_file}: {e}")
    return plugins
