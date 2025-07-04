import pytest
import os
import tempfile
import shutil
import json
from datetime import datetime
from unittest.mock import patch, MagicMock

from scraper import cli
from handlers.github_handler import GitHubHandler
from handlers.vscode_handler import VSCodeHandler
from handlers.web_handler import WebHandler
from utils.file_manager import FileManager
from utils.markdown_generator import MarkdownGenerator
from utils.config_manager import ConfigManager

class TestIntegration:
    """Integration test suite for complete application workflow"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # Create necessary directories
        os.makedirs('releases', exist_ok=True)
        os.makedirs('config', exist_ok=True)
        os.makedirs('templates', exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        
        # Create default config
        self.create_default_config()
        
    def teardown_method(self):
        """Cleanup test environment"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir)
        
    def create_default_config(self):
        """Create default configuration file"""
        config_data = {
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
        
        config_file = os.path.join(self.temp_dir, "config", "sources.json")
        with open(config_file, 'w') as f:
            json.dump(config_data, f)
            
    def test_complete_github_workflow(self):
        """Test complete GitHub scraping workflow"""
        from click.testing import CliRunner
        
        runner = CliRunner()
        
        # Mock GitHub API responses
        with patch('handlers.github_handler.Github') as mock_github:
            mock_github_instance = MagicMock()
            mock_github.return_value = mock_github_instance
            
            mock_repo = MagicMock()
            mock_github_instance.get_repo.return_value = mock_repo
            
            mock_release = MagicMock()
            mock_release.tag_name = "v1.101.0"
            mock_release.published_at = datetime(2024, 1, 1)
            mock_release.body = "Release notes content"
            mock_release.author.login = "test-author"
            mock_release.assets = []
            
            mock_repo.get_latest_release.return_value = mock_release
            
            # Execute CLI command with token to initialize GitHub client
            result = runner.invoke(cli, ['github', '--repo', 'microsoft/vscode', '--latest', '--token', 'test-token'])
            
            assert result.exit_code == 0
            
            # Verify file was created
            expected_file = os.path.join(self.temp_dir, "releases", "github", "microsoft", "vscode", "v1.101.0.md")
            assert os.path.exists(expected_file)
            
            # Verify file content
            with open(expected_file, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "# microsoft/vscode - v1.101.0" in content
                assert "Release notes content" in content
                assert "**Author**: test-author" in content
                
    def test_complete_vscode_workflow(self):
        """Test complete VS Code scraping workflow"""
        from click.testing import CliRunner
        
        runner = CliRunner()
        
        # Mock HTTP responses
        with patch('requests.get') as mock_get:
            # Mock main page response
            main_page_response = MagicMock()
            main_page_response.status_code = 200
            main_page_response.text = """
            <html>
            <body>
                <h1>May 2025 (version 1.101)</h1>
                <p>Release date: June 12, 2025</p>
            </body>
            </html>
            """
            
            # Mock version page response
            version_page_response = MagicMock()
            version_page_response.status_code = 200
            version_page_response.text = """
            <html>
            <body>
                <h1>May 2025 (version 1.101)</h1>
                <p>Release date: June 12, 2025</p>
                <h2>Chat</h2>
                <p>Chat improvements</p>
                <h2>Editor Experience</h2>
                <p>Editor improvements</p>
            </body>
            </html>
            """
            
            mock_get.side_effect = [main_page_response, version_page_response]
            
            # Execute CLI command
            result = runner.invoke(cli, ['vscode', '--latest'])
            
            assert result.exit_code == 0
            
            # Verify file was created
            expected_file = os.path.join(self.temp_dir, "releases", "vscode", "1.101.md")
            assert os.path.exists(expected_file)
            
            # Verify file content
            with open(expected_file, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "# Visual Studio Code - 1.101" in content
                assert "**Release Date**: June 12, 2025" in content
                assert "Chat improvements" in content
                assert "Editor improvements" in content
                
    def test_complete_web_workflow(self):
        """Test complete web scraping workflow"""
        from click.testing import CliRunner
        
        runner = CliRunner()
        
        # Mock HTTP response
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = """
            <html>
            <head>
                <title>Release v1.0.0 - My App</title>
            </head>
            <body>
                <h1>Release v1.0.0</h1>
                <p>Release date: January 1, 2024</p>
                <div class="content">
                    <h2>Features</h2>
                    <ul>
                        <li>New feature 1</li>
                        <li>New feature 2</li>
                    </ul>
                </div>
            </body>
            </html>
            """
            mock_get.return_value = mock_response
            
            # Execute CLI command
            result = runner.invoke(cli, [
                'web', '--url', 'https://example.com/releases/v1.0.0', '--name', 'my-app'
            ])
            
            assert result.exit_code == 0
            
            # Verify file was created
            expected_file = os.path.join(self.temp_dir, "releases", "other-sources", "my-app", "release_v100.md")
            assert os.path.exists(expected_file)
            
            # Verify file content
            with open(expected_file, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "# my-app - Release v1.0.0" in content
                assert "**Release Date**: January 1, 2024" in content
                assert "New feature 1" in content
                assert "New feature 2" in content
                
    def test_error_handling_integration(self):
        """Test error handling in integration scenarios"""
        from click.testing import CliRunner
        
        runner = CliRunner()
        
        # Test invalid repository format
        result = runner.invoke(cli, ['github', '--repo', 'invalid-repo', '--latest'])
        assert result.exit_code != 0
        
        # Test invalid version format
        result = runner.invoke(cli, ['vscode', '--version', 'invalid-version'])
        assert result.exit_code != 0
        
        # Test invalid URL format
        result = runner.invoke(cli, ['web', '--url', 'not-a-url'])
        assert result.exit_code != 0
        
    def test_configuration_integration(self):
        """Test configuration integration"""
        config_manager = ConfigManager(os.path.join(self.temp_dir, "config"))
        
        # Load configuration
        config = config_manager.load_config("sources.json")
        assert config is not None
        assert "github" in config
        assert "vscode" in config
        assert "web" in config
        
        # Get source configurations
        github_config = config_manager.get_source_config("github")
        assert github_config is not None
        assert github_config["api_base"] == "https://api.github.com"
        
        vscode_config = config_manager.get_source_config("vscode")
        assert vscode_config is not None
        assert vscode_config["base_url"] == "https://code.visualstudio.com/updates/"
    def test_file_management_integration(self):
        """Test file management integration"""
        file_manager = FileManager(self.temp_dir)
        
        # Test file path generation
        file_path = file_manager.get_file_path("github", "microsoft/vscode", "v1.101.0")
        expected_path = os.path.join(self.temp_dir, "releases", "github", "microsoft", "vscode", "v1.101.0.md")
        assert file_path == expected_path
        
        # Test markdown saving
        content = "# Test Release\n\nContent here."
        result = file_manager.save_markdown(file_path, content)
        assert result == True
        assert os.path.exists(file_path)
        
        # Test file existence check
        assert file_manager.file_exists(file_path) == True
        
    def test_markdown_generation_integration(self):
        """Test markdown generation integration"""
        generator = MarkdownGenerator()
        
        # Test GitHub markdown generation
        release_data = {
            'version': 'v1.101.0',
            'date': datetime(2024, 1, 1),
            'content': 'Release notes content',
            'author': 'test-author'
        }
        
        markdown = generator.generate_github_release_markdown("microsoft/vscode", release_data)
        assert "# microsoft/vscode - v1.101.0" in markdown
        assert "Release notes content" in markdown
        
        # Test VS Code markdown generation
        vscode_data = {
            'version': '1.101',
            'date': 'June 12, 2025',
            'content': 'VS Code content'
        }
        
        vscode_markdown = generator.generate_vscode_release_markdown(vscode_data)
        assert "# Visual Studio Code - 1.101" in vscode_markdown
        assert "VS Code content" in vscode_markdown
        
    def test_handler_integration(self):
        """Test handler integration"""
        # Test GitHub handler
        github_handler = GitHubHandler()
        assert github_handler.validate_repo_format("microsoft/vscode") == True
        assert github_handler.validate_repo_format("invalid-repo") == False
        
        # Test VS Code handler
        vscode_handler = VSCodeHandler()
        assert vscode_handler.validate_version_format("1.101") == True
        assert vscode_handler.validate_version_format("invalid-version") == False
        assert vscode_handler.convert_version_to_url_format("1.101") == "v1_101"
        
        # Test web handler
        web_handler = WebHandler()
        assert web_handler.validate_url_format("https://example.com") == True
        assert web_handler.validate_url_format("not-a-url") == False
        assert web_handler.extract_name_from_url("https://example.com/releases/v1.0.0") == "example.com"
        
    def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow"""
        from click.testing import CliRunner
        
        runner = CliRunner()
        
        # Test GitHub workflow with mocked API
        with patch('handlers.github_handler.Github') as mock_github:
            mock_github_instance = MagicMock()
            mock_github.return_value = mock_github_instance
            
            mock_repo = MagicMock()
            mock_github_instance.get_repo.return_value = mock_repo
            
            mock_release = MagicMock()
            mock_release.tag_name = "v1.101.0"
            mock_release.published_at = datetime(2024, 1, 1)
            mock_release.body = "Release notes content"
            mock_release.author.login = "test-author"
            mock_release.assets = []
            
            mock_repo.get_latest_release.return_value = mock_release
            
            result = runner.invoke(cli, ['github', '--repo', 'microsoft/vscode', '--latest', '--token', 'test-token'])
            assert result.exit_code == 0
            
        # Test VS Code workflow with mocked HTTP
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = """
            <html>
            <body>
                <h1>May 2025 (version 1.101)</h1>
                <p>Release date: June 12, 2025</p>
                <h2>Features</h2>
                <p>New features</p>
            </body>
            </html>
            """
            mock_get.return_value = mock_response
            
            result = runner.invoke(cli, ['vscode', '--version', '1.101'])
            assert result.exit_code == 0
            
        # Verify files were created
        github_file = os.path.join(self.temp_dir, "releases", "github", "microsoft", "vscode", "v1.101.0.md")
        vscode_file = os.path.join(self.temp_dir, "releases", "vscode", "1.101.md")
        
        assert os.path.exists(github_file)
        assert os.path.exists(vscode_file) 
