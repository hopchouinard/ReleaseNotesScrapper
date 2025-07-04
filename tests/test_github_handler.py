import pytest
from unittest.mock import patch, MagicMock, Mock
import json
import os
from datetime import datetime

from handlers.github_handler import GitHubHandler

class TestGitHubHandler:
    """Test suite for GitHub handler"""
    
    def setup_method(self):
        """Setup test environment"""
        self.handler = GitHubHandler()
        self.mock_repo = "microsoft/vscode"
        self.mock_version = "v1.101.0"
        
    def test_init_without_token(self):
        """Test handler initialization without token"""
        handler = GitHubHandler()
        assert handler.github is None
        assert handler.repo_name is None
        
    def test_init_with_token(self):
        """Test handler initialization with token"""
        with patch('handlers.github_handler.Github') as mock_github:
            handler = GitHubHandler(token="test-token")
            mock_github.assert_called_once_with("test-token")
            
    def test_validate_repo_format_valid(self):
        """Test valid repository format validation"""
        assert self.handler.validate_repo_format("owner/repo") == True
        assert self.handler.validate_repo_format("microsoft/vscode") == True
        
    def test_validate_repo_format_invalid(self):
        """Test invalid repository format validation"""
        assert self.handler.validate_repo_format("invalid-repo") == False
        assert self.handler.validate_repo_format("owner/repo/subdir") == False
        assert self.handler.validate_repo_format("") == False
        
    def test_setup_repo_success(self):
        """Test successful repository setup"""
        with patch('handlers.github_handler.Github') as mock_github:
            mock_github_instance = MagicMock()
            mock_github.return_value = mock_github_instance
            mock_repo = MagicMock()
            mock_github_instance.get_repo.return_value = mock_repo
            
            handler = GitHubHandler(token="test-token")
            result = handler.setup_repo(self.mock_repo)
            
            assert result == True
            assert handler.repo == mock_repo
            assert handler.repo_name == "microsoft/vscode"
            
    def test_setup_repo_failure(self):
        """Test repository setup failure"""
        with patch('handlers.github_handler.Github') as mock_github:
            mock_github_instance = MagicMock()
            mock_github.return_value = mock_github_instance
            mock_github_instance.get_repo.side_effect = Exception("Repo not found")
            
            handler = GitHubHandler(token="test-token")
            result = handler.setup_repo(self.mock_repo)
            
            assert result == False
            
    def test_get_latest_release_success(self):
        """Test successful latest release retrieval"""
        with patch.object(self.handler, 'setup_repo') as mock_setup:
            mock_setup.return_value = True
            
            mock_repo = MagicMock()
            mock_release = MagicMock()
            mock_release.tag_name = "v1.101.0"
            mock_release.published_at = datetime(2024, 1, 1)
            mock_release.body = "Release notes content"
            mock_repo.get_latest_release.return_value = mock_release
            
            self.handler.repo = mock_repo
            
            result = self.handler.get_latest_release(self.mock_repo)
            
            assert result is not None
            assert result['version'] == "v1.101.0"
            assert result['date'] == datetime(2024, 1, 1)
            assert result['content'] == "Release notes content"
            
    def test_get_latest_release_failure(self):
        """Test latest release retrieval failure"""
        with patch.object(self.handler, 'setup_repo') as mock_setup:
            mock_setup.return_value = False
            
            result = self.handler.get_latest_release(self.mock_repo)
            assert result is None
            
    def test_get_release_by_version_success(self):
        """Test successful release retrieval by version"""
        with patch.object(self.handler, 'setup_repo') as mock_setup:
            mock_setup.return_value = True
            
            mock_repo = MagicMock()
            mock_release = MagicMock()
            mock_release.tag_name = "v1.101.0"
            mock_release.published_at = datetime(2024, 1, 1)
            mock_release.body = "Release notes content"
            mock_repo.get_release.return_value = mock_release
            
            self.handler.repo = mock_repo
            
            result = self.handler.get_release_by_version(self.mock_repo, self.mock_version)
            
            assert result is not None
            assert result['version'] == "v1.101.0"
            assert result['date'] == datetime(2024, 1, 1)
            assert result['content'] == "Release notes content"
            
    def test_get_release_by_version_failure(self):
        """Test release retrieval by version failure"""
        with patch.object(self.handler, 'setup_repo') as mock_setup:
            mock_setup.return_value = False
            
            result = self.handler.get_release_by_version(self.mock_repo, self.mock_version)
            assert result is None
            
    def test_get_all_releases_success(self):
        """Test successful all releases retrieval"""
        with patch.object(self.handler, 'setup_repo') as mock_setup:
            mock_setup.return_value = True
            
            mock_repo = MagicMock()
            mock_release1 = MagicMock()
            mock_release1.tag_name = "v1.101.0"
            mock_release1.published_at = datetime(2024, 1, 1)
            mock_release1.body = "Release notes 1"
            
            mock_release2 = MagicMock()
            mock_release2.tag_name = "v1.100.0"
            mock_release2.published_at = datetime(2023, 12, 1)
            mock_release2.body = "Release notes 2"
            
            mock_repo.get_releases.return_value = [mock_release1, mock_release2]
            
            self.handler.repo = mock_repo
            
            result = self.handler.get_all_releases(self.mock_repo)
            
            assert len(result) == 2
            assert result[0]['version'] == "v1.101.0"
            assert result[1]['version'] == "v1.100.0"
            
    def test_get_releases_by_date_range_success(self):
        """Test successful releases retrieval by date range"""
        with patch.object(self.handler, 'setup_repo') as mock_setup:
            mock_setup.return_value = True
            
            mock_repo = MagicMock()
            mock_release = MagicMock()
            mock_release.tag_name = "v1.101.0"
            mock_release.published_at = datetime(2024, 1, 15)
            mock_release.body = "Release notes content"
            
            mock_repo.get_releases.return_value = [mock_release]
            
            self.handler.repo = mock_repo
            
            result = self.handler.get_releases_by_date_range(
                self.mock_repo, "2024-01-01", "2024-01-31"
            )
            
            assert len(result) == 1
            assert result[0]['version'] == "v1.101.0"
            
    def test_scrape_latest_success(self):
        """Test successful latest release scraping"""
        with patch.object(self.handler, 'get_latest_release') as mock_get:
            with patch.object(self.handler, 'save_release') as mock_save:
                mock_get.return_value = {
                    'version': 'v1.101.0',
                    'date': datetime(2024, 1, 1),
                    'content': 'Release notes content'
                }
                mock_save.return_value = True
                
                result = self.handler.scrape_latest(self.mock_repo)
                assert result == True
                mock_get.assert_called_once_with(self.mock_repo)
                mock_save.assert_called_once()
                
    def test_scrape_version_success(self):
        """Test successful specific version scraping"""
        with patch.object(self.handler, 'get_release_by_version') as mock_get:
            with patch.object(self.handler, 'save_release') as mock_save:
                mock_get.return_value = {
                    'version': 'v1.101.0',
                    'date': datetime(2024, 1, 1),
                    'content': 'Release notes content'
                }
                mock_save.return_value = True
                
                result = self.handler.scrape_version(self.mock_repo, self.mock_version)
                assert result == True
                mock_get.assert_called_once_with(self.mock_repo, self.mock_version)
                mock_save.assert_called_once()
                
    def test_scrape_all_success(self):
        """Test successful all releases scraping"""
        with patch.object(self.handler, 'get_all_releases') as mock_get:
            with patch.object(self.handler, 'save_release') as mock_save:
                mock_get.return_value = [
                    {
                        'version': 'v1.101.0',
                        'date': datetime(2024, 1, 1),
                        'content': 'Release notes 1'
                    },
                    {
                        'version': 'v1.100.0',
                        'date': datetime(2023, 12, 1),
                        'content': 'Release notes 2'
                    }
                ]
                mock_save.return_value = True
                
                result = self.handler.scrape_all(self.mock_repo)
                assert result == True
                mock_get.assert_called_once_with(self.mock_repo)
                assert mock_save.call_count == 2
                
    def test_scrape_date_range_success(self):
        """Test successful date range scraping"""
        with patch.object(self.handler, 'get_releases_by_date_range') as mock_get:
            with patch.object(self.handler, 'save_release') as mock_save:
                mock_get.return_value = [
                    {
                        'version': 'v1.101.0',
                        'date': datetime(2024, 1, 15),
                        'content': 'Release notes content'
                    }
                ]
                mock_save.return_value = True
                
                result = self.handler.scrape_date_range(self.mock_repo, "2024-01-01", "2024-01-31")
                assert result == True
                mock_get.assert_called_once_with(self.mock_repo, "2024-01-01", "2024-01-31")
                mock_save.assert_called_once()
                
    def test_save_release_success(self):
        """Test successful release saving"""
        with patch('utils.file_manager.FileManager.save_markdown') as mock_save:
            mock_save.return_value = True
            
            release_data = {
                'version': 'v1.101.0',
                'date': datetime(2024, 1, 1),
                'content': 'Release notes content'
            }
            
            result = self.handler.save_release(self.mock_repo, release_data)
            assert result == True
            mock_save.assert_called_once()
            
    def test_rate_limit_handling(self):
        """Test rate limit handling"""
        with patch('handlers.github_handler.Github') as mock_github:
            mock_github_instance = MagicMock()
            mock_github.return_value = mock_github_instance
            mock_github_instance.get_repo.side_effect = Exception("API rate limit exceeded")
            
            handler = GitHubHandler(token="test-token")
            result = handler.setup_repo(self.mock_repo)
            
            assert result == False 
