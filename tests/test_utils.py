import pytest
import os
import tempfile
import shutil
import json
from datetime import datetime
from unittest.mock import patch, MagicMock

from utils.file_manager import FileManager
from utils.markdown_generator import MarkdownGenerator
from utils.config_manager import ConfigManager

class TestFileManager:
    """Test suite for FileManager"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.file_manager = FileManager(self.temp_dir)
        
    def teardown_method(self):
        """Cleanup test environment"""
        shutil.rmtree(self.temp_dir)
        
    def test_init(self):
        """Test FileManager initialization"""
        assert self.file_manager.base_dir == self.temp_dir
        
    def test_create_directory_success(self):
        """Test successful directory creation"""
        test_dir = os.path.join(self.temp_dir, "test_dir")
        result = self.file_manager.create_directory(test_dir)
        
        assert result == True
        assert os.path.exists(test_dir)
        
    def test_create_directory_already_exists(self):
        """Test directory creation when already exists"""
        test_dir = os.path.join(self.temp_dir, "test_dir")
        os.makedirs(test_dir, exist_ok=True)
        
        result = self.file_manager.create_directory(test_dir)
        assert result == True
        
    def test_create_directory_failure(self):
        """Test directory creation failure (skipped on Windows: not reliably testable)"""
        import sys
        if sys.platform.startswith('win'):
            pytest.skip("Permission errors are not reliably testable on Windows.")
        # Unix: Try to create in a non-existent parent directory or protected location
        test_dir = "/root/should_fail_dir"
        result = self.file_manager.create_directory(test_dir)
        assert result == False
        
    def test_save_markdown_success(self):
        """Test successful markdown saving"""
        content = "# Test Release\n\nThis is a test release."
        file_path = os.path.join(self.temp_dir, "test.md")
        
        result = self.file_manager.save_markdown(file_path, content)
        
        assert result == True
        assert os.path.exists(file_path)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            saved_content = f.read()
            assert saved_content == content
            
    def test_save_markdown_directory_creation(self):
        """Test markdown saving with directory creation"""
        content = "# Test Release\n\nThis is a test release."
        file_path = os.path.join(self.temp_dir, "subdir", "test.md")
        
        result = self.file_manager.save_markdown(file_path, content)
        
        assert result == True
        assert os.path.exists(file_path)
        
    def test_save_markdown_failure(self):
        """Test markdown saving failure (skipped on Windows: not reliably testable)"""
        import sys
        if sys.platform.startswith('win'):
            pytest.skip("Permission errors are not reliably testable on Windows.")
        content = "# Test Release\n\nThis is a test release."
        file_path = "/root/should_fail.md"
        result = self.file_manager.save_markdown(file_path, content)
        assert result == False
        
    def test_file_exists(self):
        """Test file existence check"""
        file_path = os.path.join(self.temp_dir, "test.md")
        
        # File doesn't exist
        assert self.file_manager.file_exists(file_path) == False
        
        # Create file
        with open(file_path, 'w') as f:
            f.write("test")
            
        # File exists
        assert self.file_manager.file_exists(file_path) == True
        
    def test_get_file_path(self):
        """Test file path generation"""
        source_type = "github"
        project_name = "microsoft/vscode"
        version = "v1.101.0"
        
        expected_path = os.path.join(self.temp_dir, "releases", "github", "microsoft", "vscode", "v1.101.0.md")
        result_path = self.file_manager.get_file_path(source_type, project_name, version)
        
        assert result_path == expected_path
        
    def test_clean_filename(self):
        """Test filename cleaning"""
        dirty_name = "file/with\\invalid:chars*?"
        clean_name = self.file_manager.clean_filename(dirty_name)
        
        assert "/" not in clean_name
        assert "\\" not in clean_name
        assert ":" not in clean_name
        assert "*" not in clean_name
        assert "?" not in clean_name

class TestMarkdownGenerator:
    """Test suite for MarkdownGenerator"""
    
    def setup_method(self):
        """Setup test environment"""
        self.generator = MarkdownGenerator()
        
    def test_generate_github_release_markdown(self):
        """Test GitHub release markdown generation"""
        release_data = {
            'version': 'v1.101.0',
            'date': datetime(2024, 1, 1),
            'content': 'Release notes content',
            'author': 'test-author',
            'assets': ['asset1.zip', 'asset2.zip']
        }
        
        markdown = self.generator.generate_github_release_markdown(
            "microsoft/vscode", release_data
        )
        
        assert "# microsoft/vscode - v1.101.0" in markdown
        assert "**Release Date**: 2024-01-01" in markdown
        assert "Release notes content" in markdown
        assert "**Author**: test-author" in markdown
        assert "asset1.zip" in markdown
        assert "asset2.zip" in markdown
        
    def test_generate_vscode_release_markdown(self):
        """Test VS Code release markdown generation"""
        release_data = {
            'version': '1.101',
            'date': 'June 12, 2025',
            'content': 'VS Code release content'
        }
        
        markdown = self.generator.generate_vscode_release_markdown(release_data)
        
        assert "# Visual Studio Code - 1.101" in markdown
        assert "**Release Date**: June 12, 2025" in markdown
        assert "VS Code release content" in markdown
        assert "https://code.visualstudio.com/updates/v1_101" in markdown
        
    def test_generate_web_release_markdown(self):
        """Test web release markdown generation"""
        release_data = {
            'title': 'Release v1.0.0',
            'date': 'January 1, 2024',
            'content': 'Web release content'
        }
        
        markdown = self.generator.generate_web_release_markdown(
            "my-app", release_data, "https://example.com/releases/v1.0.0"
        )
        
        assert "# my-app - Release v1.0.0" in markdown
        assert "**Release Date**: January 1, 2024" in markdown
        assert "Web release content" in markdown
        assert "https://example.com/releases/v1.0.0" in markdown
        
    def test_format_content_sections(self):
        """Test content section formatting"""
        sections = {
            'Features': 'New features added',
            'Bug Fixes': 'Bugs fixed',
            'Breaking Changes': 'Breaking changes'
        }
        
        formatted = self.generator.format_content_sections(sections)
        
        assert "## Features" in formatted
        assert "New features added" in formatted
        assert "## Bug Fixes" in formatted
        assert "Bugs fixed" in formatted
        assert "## Breaking Changes" in formatted
        assert "Breaking changes" in formatted
        
    def test_clean_markdown_content(self):
        """Test markdown content cleaning"""
        dirty_content = """
        <script>alert('test');</script>
        <h1>Title</h1>
        <p>Content with <strong>bold</strong> text.</p>
        <ul>
            <li>Item 1</li>
            <li>Item 2</li>
        </ul>
        """
        
        cleaned = self.generator.clean_markdown_content(dirty_content)
        
        assert "script" not in cleaned.lower()
        assert "# Title" in cleaned
        assert "**bold**" in cleaned
        assert "- Item 1" in cleaned
        assert "- Item 2" in cleaned
        
    def test_add_metadata(self):
        """Test metadata addition"""
        content = "# Test Release\n\nContent here."
        metadata = {
            'source': 'https://example.com',
            'scraped': datetime(2024, 1, 1, 12, 0, 0)
        }
        
        result = self.generator.add_metadata(content, metadata)
        
        assert "**Source**: https://example.com" in result
        assert "**Scraped**: 2024-01-01 12:00:00" in result
        assert "*Scraped from https://example.com on 2024-01-01 12:00:00*" in result

class TestConfigManager:
    """Test suite for ConfigManager"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_manager = ConfigManager(self.temp_dir)
        
    def teardown_method(self):
        """Cleanup test environment"""
        shutil.rmtree(self.temp_dir)
        
    def test_init(self):
        """Test ConfigManager initialization"""
        assert self.config_manager.config_dir == self.temp_dir
        
    def test_load_config_success(self):
        """Test successful config loading"""
        config_data = {
            "github": {
                "api_base": "https://api.github.com",
                "file_directory": "releases/github"
            },
            "vscode": {
                "base_url": "https://code.visualstudio.com/updates/",
                "file_directory": "releases/vscode"
            }
        }
        
        config_file = os.path.join(self.temp_dir, "sources.json")
        with open(config_file, 'w') as f:
            json.dump(config_data, f)
            
        result = self.config_manager.load_config("sources.json")
        
        assert result == config_data
        
    def test_load_config_file_not_found(self):
        """Test config loading when file not found"""
        result = self.config_manager.load_config("nonexistent.json")
        assert result is None
        
    def test_load_config_invalid_json(self):
        """Test config loading with invalid JSON"""
        config_file = os.path.join(self.temp_dir, "invalid.json")
        with open(config_file, 'w') as f:
            f.write("invalid json content")
            
        result = self.config_manager.load_config("invalid.json")
        assert result is None
        
    def test_save_config_success(self):
        """Test successful config saving"""
        config_data = {
            "github": {
                "api_base": "https://api.github.com",
                "file_directory": "releases/github"
            }
        }
        
        result = self.config_manager.save_config("test_config.json", config_data)
        
        assert result == True
        
        # Verify the file was created and contains correct data
        config_file = os.path.join(self.temp_dir, "test_config.json")
        assert os.path.exists(config_file)
        
        with open(config_file, 'r') as f:
            saved_data = json.load(f)
            assert saved_data == config_data
            
    def test_save_config_failure(self):
        """Test config saving failure (skipped on Windows: not reliably testable)"""
        import sys
        if sys.platform.startswith('win'):
            pytest.skip("Permission errors are not reliably testable on Windows.")
        config_data = {"test": "data"}
        result = self.config_manager.save_config("/root/should_fail_config.json", config_data)
        assert result == False
        
    def test_get_source_config(self):
        """Test getting source configuration"""
        config_data = {
            "github": {
                "api_base": "https://api.github.com",
                "file_directory": "releases/github"
            },
            "vscode": {
                "base_url": "https://code.visualstudio.com/updates/",
                "file_directory": "releases/vscode"
            }
        }
        
        with patch.object(self.config_manager, 'load_config') as mock_load:
            mock_load.return_value = config_data
            
            github_config = self.config_manager.get_source_config("github")
            vscode_config = self.config_manager.get_source_config("vscode")
            
            assert github_config == config_data["github"]
            assert vscode_config == config_data["vscode"]
            
    def test_get_source_config_not_found(self):
        """Test getting source configuration when not found"""
        config_data = {
            "github": {
                "api_base": "https://api.github.com"
            }
        }
        
        with patch.object(self.config_manager, 'load_config') as mock_load:
            mock_load.return_value = config_data
            
            result = self.config_manager.get_source_config("nonexistent")
            assert result is None
            
    def test_validate_config_structure(self):
        """Test config structure validation"""
        valid_config = {
            "github": {
                "api_base": "https://api.github.com",
                "file_directory": "releases/github"
            }
        }
        
        invalid_config = {
            "github": "invalid_structure"
        }
        
        assert self.config_manager.validate_config_structure(valid_config) == True
        assert self.config_manager.validate_config_structure(invalid_config) == False
        
    def test_get_default_config(self):
        """Test getting default configuration"""
        default_config = self.config_manager.get_default_config()
        
        assert "github" in default_config
        assert "vscode" in default_config
        assert "web" in default_config
        assert default_config["github"]["api_base"] == "https://api.github.com"
        assert default_config["vscode"]["base_url"] == "https://code.visualstudio.com/updates/" 
