import pytest
import click
from click.testing import CliRunner
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock
import json

# Import the main CLI application
from scraper import cli

class TestCLI:
    """Test suite for CLI functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # Create necessary directories
        os.makedirs('releases', exist_ok=True)
        os.makedirs('config', exist_ok=True)
        os.makedirs('templates', exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        
    def teardown_method(self):
        """Cleanup test environment"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir)
    
    def test_cli_help(self):
        """Test CLI help command"""
        result = self.runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'Usage:' in result.output
        assert 'github' in result.output
        assert 'vscode' in result.output
        assert 'web' in result.output
    
    def test_cli_no_args(self):
        """Test CLI with no arguments"""
        result = self.runner.invoke(cli, [])
        assert result.exit_code != 0  # Should fail without source
    
    def test_github_latest_command(self):
        """Test GitHub latest command"""
        with patch('handlers.github_handler.GitHubHandler.scrape_latest') as mock_scrape:
            mock_scrape.return_value = True
            result = self.runner.invoke(cli, ['github', '--repo', 'microsoft/vscode', '--latest'])
            assert result.exit_code == 0
            mock_scrape.assert_called_once()
    
    def test_github_specific_version(self):
        """Test GitHub specific version command"""
        with patch('handlers.github_handler.GitHubHandler.scrape_version') as mock_scrape:
            mock_scrape.return_value = True
            result = self.runner.invoke(cli, ['github', '--repo', 'microsoft/vscode', '--version', 'v1.101.0'])
            assert result.exit_code == 0
            mock_scrape.assert_called_once_with('microsoft/vscode', 'v1.101.0')
    
    def test_github_all_releases(self):
        """Test GitHub all releases command"""
        with patch('handlers.github_handler.GitHubHandler.scrape_all') as mock_scrape:
            mock_scrape.return_value = True
            result = self.runner.invoke(cli, ['github', '--repo', 'microsoft/vscode', '--all'])
            assert result.exit_code == 0
            mock_scrape.assert_called_once()
    
    def test_github_date_range(self):
        """Test GitHub date range command"""
        with patch('handlers.github_handler.GitHubHandler.scrape_date_range') as mock_scrape:
            mock_scrape.return_value = True
            result = self.runner.invoke(cli, [
                'github', '--repo', 'microsoft/vscode', 
                '--from', '2024-01-01', '--to', '2024-12-31'
            ])
            assert result.exit_code == 0
            mock_scrape.assert_called_once_with('microsoft/vscode', '2024-01-01', '2024-12-31')
    
    def test_vscode_latest_command(self):
        """Test VS Code latest command"""
        with patch('handlers.vscode_handler.VSCodeHandler.scrape_latest') as mock_scrape:
            mock_scrape.return_value = True
            result = self.runner.invoke(cli, ['vscode', '--latest'])
            assert result.exit_code == 0
            mock_scrape.assert_called_once()
    
    def test_vscode_specific_version(self):
        """Test VS Code specific version command"""
        with patch('handlers.vscode_handler.VSCodeHandler.scrape_version') as mock_scrape:
            mock_scrape.return_value = True
            result = self.runner.invoke(cli, ['vscode', '--version', '1.101'])
            assert result.exit_code == 0
            mock_scrape.assert_called_once_with('1.101')
    
    def test_vscode_all_versions(self):
        """Test VS Code all versions command"""
        with patch('handlers.vscode_handler.VSCodeHandler.scrape_all') as mock_scrape:
            mock_scrape.return_value = True
            result = self.runner.invoke(cli, ['vscode', '--all'])
            assert result.exit_code == 0
            mock_scrape.assert_called_once()
    
    def test_vscode_version_range(self):
        """Test VS Code version range command"""
        with patch('handlers.vscode_handler.VSCodeHandler.scrape_version_range') as mock_scrape:
            mock_scrape.return_value = True
            result = self.runner.invoke(cli, ['vscode', '--from', '1.100', '--to', '1.101'])
            assert result.exit_code == 0
            mock_scrape.assert_called_once_with('1.100', '1.101')
    
    def test_web_specific_url(self):
        """Test web specific URL command"""
        with patch('handlers.web_handler.WebHandler.scrape_url') as mock_scrape:
            mock_scrape.return_value = True
            result = self.runner.invoke(cli, ['web', '--url', 'https://example.com/releases/v1.0.0'])
            assert result.exit_code == 0
            mock_scrape.assert_called_once_with('https://example.com/releases/v1.0.0', None)
    
    def test_web_url_with_name(self):
        """Test web URL with custom name command"""
        with patch('handlers.web_handler.WebHandler.scrape_url') as mock_scrape:
            mock_scrape.return_value = True
            result = self.runner.invoke(cli, [
                'web', '--url', 'https://example.com/releases/v1.0.0', '--name', 'my-app'
            ])
            assert result.exit_code == 0
            mock_scrape.assert_called_once_with('https://example.com/releases/v1.0.0', 'my-app')
    
    def test_invalid_github_repo(self):
        """Test invalid GitHub repository format"""
        result = self.runner.invoke(cli, ['github', '--repo', 'invalid-repo', '--latest'])
        assert result.exit_code != 0
    
    def test_missing_required_args(self):
        """Test missing required arguments"""
        result = self.runner.invoke(cli, ['github'])  # Missing --repo
        assert result.exit_code != 0
        
        result = self.runner.invoke(cli, ['vscode'])  # Missing action
        assert result.exit_code != 0
        
        result = self.runner.invoke(cli, ['web'])  # Missing --url
        assert result.exit_code != 0
    
    def test_invalid_version_format(self):
        """Test invalid version format"""
        result = self.runner.invoke(cli, ['vscode', '--version', 'invalid-version'])
        assert result.exit_code != 0
    
    def test_invalid_date_format(self):
        """Test invalid date format"""
        result = self.runner.invoke(cli, [
            'github', '--repo', 'microsoft/vscode', 
            '--from', 'invalid-date', '--to', '2024-12-31'
        ])
        assert result.exit_code != 0
    
    def test_invalid_url_format(self):
        """Test invalid URL format"""
        result = self.runner.invoke(cli, ['web', '--url', 'not-a-url'])
        assert result.exit_code != 0 
