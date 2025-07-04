import json
import os
from typing import Dict, Any, Optional

class ConfigManager:
    """Manages configuration loading and validation"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = config_dir
        
    def load_config(self, filename: str) -> Optional[Dict[str, Any]]:
        """Load configuration from JSON file"""
        try:
            # Support absolute or relative path
            config_path = filename if os.path.isabs(filename) else os.path.join(self.config_dir, filename)
            if not os.path.exists(config_path):
                return None
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            if self.validate_config_structure(config):
                return config
            else:
                return None
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading config: {e}")
            return None
            
    def save_config(self, filename: str, config: Dict[str, Any]) -> bool:
        """Save configuration to JSON file"""
        try:
            config_path = filename if os.path.isabs(filename) else os.path.join(self.config_dir, filename)
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            return True
        except (IOError, OSError) as e:
            print(f"Error saving config: {e}")
            return False
            
    def get_source_config(self, source_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific source"""
        config = self.load_config("sources.json")
        if config and source_name in config:
            return config[source_name]
        return None
        
    def validate_config_structure(self, config: Dict[str, Any]) -> bool:
        """Validate configuration structure: all top-level values must be dicts"""
        if not isinstance(config, dict):
            return False
        for value in config.values():
            if not isinstance(value, dict):
                return False
        return True
        
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "github": {
                "api_base": "https://api.github.com",
                "file_directory": "releases/github",
                "template": "templates/github_template.md",
                "rate_limit": {
                    "requests_per_hour": 5000,
                    "requests_per_minute": 60
                }
            },
            "vscode": {
                "base_url": "https://code.visualstudio.com/updates/",
                "version_url_pattern": "https://code.visualstudio.com/updates/v{version}",
                "file_directory": "releases/vscode",
                "template": "templates/vscode_template.md",
                "version_format": "underscore"
            },
            "web": {
                "file_directory": "releases/other-sources",
                "template": "templates/web_template.md"
            }
        } 
