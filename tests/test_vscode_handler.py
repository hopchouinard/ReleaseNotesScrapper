import pytest
from unittest.mock import patch, MagicMock, Mock
import json
import os
from datetime import datetime
from bs4 import BeautifulSoup

from handlers.vscode_handler import VSCodeHandler

class TestVSCodeHandler:
    """Test suite for VS Code handler"""
    
    def setup_method(self):
        """Setup test environment"""
        self.handler = VSCodeHandler()
        self.mock_version = "1.101"
        self.base_url = "https://code.visualstudio.com/updates/"
        
    def test_init(self):
        """Test handler initialization"""
        assert self.handler.base_url == "https://code.visualstudio.com/updates/"
        assert self.handler.version_url_pattern == "https://code.visualstudio.com/updates/{version}"
        
    def test_validate_version_format_valid(self):
        """Test valid version format validation"""
        assert self.handler.validate_version_format("1.101") == True
        assert self.handler.validate_version_format("1.100") == True
        assert self.handler.validate_version_format("1.99") == True
        
    def test_validate_version_format_invalid(self):
        """Test invalid version format validation"""
        assert self.handler.validate_version_format("invalid-version") == False
        assert self.handler.validate_version_format("v1.101") == False
        assert self.handler.validate_version_format("1.101.0") == False
        assert self.handler.validate_version_format("") == False
        
    def test_convert_version_to_url_format(self):
        """Test version to URL format conversion"""
        assert self.handler.convert_version_to_url_format("1.101") == "v1_101"
        assert self.handler.convert_version_to_url_format("1.100") == "v1_100"
        assert self.handler.convert_version_to_url_format("1.99") == "v1_99"
        
    def test_build_version_url(self):
        """Test version URL building"""
        expected_url = "https://code.visualstudio.com/updates/v1_101"
        assert self.handler.build_version_url("1.101") == expected_url
        
    def test_fetch_page_success(self):
        """Test successful page fetching"""
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = "<html><body>Test content</body></html>"
            mock_get.return_value = mock_response
            
            result = self.handler.fetch_page(self.base_url)
            
            assert result is not None
            assert result.status_code == 200
            mock_get.assert_called_once_with(self.base_url, timeout=30)
            
    def test_fetch_page_failure(self):
        """Test page fetching failure"""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = Exception("Network error")
            
            result = self.handler.fetch_page(self.base_url)
            assert result is None
            mock_get.assert_called_once_with(self.base_url, timeout=30)
            
    def test_parse_latest_version_from_main_page(self):
        """Test parsing latest version from main page"""
        html_content = """
        <html>
        <body>
            <h1>May 2025 (version 1.101)</h1>
            <p>Release date: June 12, 2025</p>
        </body>
        </html>
        """
        
        with patch.object(self.handler, 'fetch_page') as mock_fetch:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = html_content
            mock_fetch.return_value = mock_response
            
            result = self.handler.parse_latest_version_from_main_page()
            
            assert result == "1.101"
            
    def test_parse_latest_version_not_found(self):
        """Test parsing latest version when not found"""
        html_content = "<html><body>No version information</body></html>"
        
        with patch.object(self.handler, 'fetch_page') as mock_fetch:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = html_content
            mock_fetch.return_value = mock_response
            
            result = self.handler.parse_latest_version_from_main_page()
            
            assert result is None
            
    def test_parse_version_page_content(self):
        """Test parsing version page content"""
        html_content = """
        <html>
        <body>
            <h1>May 2025 (version 1.101)</h1>
            <p>Release date: June 12, 2025</p>
            <h2>Chat</h2>
            <p>Chat improvements</p>
            <h2>Editor Experience</h2>
            <p>Editor improvements</p>
            <h2>Notable fixes</h2>
            <p>Bug fixes</p>
            <h2>Thank you</h2>
            <p>Contributors list</p>
        </body>
        </html>
        """
        
        with patch.object(self.handler, 'fetch_page') as mock_fetch:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = html_content
            mock_fetch.return_value = mock_response
            
            result = self.handler.parse_version_page_content("1.101")
            
            assert result is not None
            assert result['version'] == "1.101"
            assert result['date'] == "June 12, 2025"
            assert 'Chat' in result['content']
            assert 'Editor Experience' in result['content']
            assert 'Notable fixes' in result['content']
            assert 'Thank you' in result['content']
            
    def test_parse_version_page_not_found(self):
        """Test parsing version page when not found"""
        with patch.object(self.handler, 'fetch_page') as mock_fetch:
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_fetch.return_value = mock_response
            
            result = self.handler.parse_version_page_content("1.101")
            
            assert result is None
            
    def test_extract_sections_from_content(self):
        """Test extracting sections from content"""
        html_content = """
        <h2>Chat</h2>
        <p>Chat improvements</p>
        <h2>Editor Experience</h2>
        <p>Editor improvements</p>
        <h2>Notable fixes</h2>
        <p>Bug fixes</p>
        """
        
        soup = BeautifulSoup(html_content, 'html.parser')
        sections = self.handler.extract_sections_from_content(soup)
        
        assert 'Chat' in sections
        assert 'Editor Experience' in sections
        assert 'Notable fixes' in sections
        assert sections['Chat'].strip() == 'Chat improvements'
        assert sections['Editor Experience'].strip() == 'Editor improvements'
        
    def test_get_available_versions_from_main_page(self):
        """Test getting available versions from main page"""
        html_content = """
        <html>
        <body>
            <ul>
                <li><a href="/updates/v1_101">May 2025</a></li>
                <li><a href="/updates/v1_100">April 2025</a></li>
                <li><a href="/updates/v1_99">March 2025</a></li>
            </ul>
        </body>
        </html>
        """
        
        with patch.object(self.handler, 'fetch_page') as mock_fetch:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = html_content
            mock_fetch.return_value = mock_response
            
            result = self.handler.get_available_versions_from_main_page()
            
            assert len(result) == 3
            assert "1.101" in result
            assert "1.100" in result
            assert "1.99" in result
            
    def test_scrape_latest_success(self):
        """Test successful latest version scraping"""
        with patch.object(self.handler, 'parse_latest_version_from_main_page') as mock_parse:
            with patch.object(self.handler, 'scrape_version') as mock_scrape:
                mock_parse.return_value = "1.101"
                mock_scrape.return_value = True
                
                result = self.handler.scrape_latest()
                
                assert result == True
                mock_parse.assert_called_once()
                mock_scrape.assert_called_once_with("1.101")
                
    def test_scrape_latest_failure(self):
        """Test latest version scraping failure"""
        with patch.object(self.handler, 'parse_latest_version_from_main_page') as mock_parse:
            mock_parse.return_value = None
            
            result = self.handler.scrape_latest()
            
            assert result == False
            
    def test_scrape_version_success(self):
        """Test successful specific version scraping"""
        with patch.object(self.handler, 'parse_version_page_content') as mock_parse:
            with patch.object(self.handler, 'save_release') as mock_save:
                mock_parse.return_value = {
                    'version': '1.101',
                    'date': 'June 12, 2025',
                    'content': 'Release notes content'
                }
                mock_save.return_value = True
                
                result = self.handler.scrape_version("1.101")
                
                assert result == True
                mock_parse.assert_called_once_with("1.101")
                mock_save.assert_called_once()
                
    def test_scrape_version_failure(self):
        """Test specific version scraping failure"""
        with patch.object(self.handler, 'parse_version_page_content') as mock_parse:
            mock_parse.return_value = None
            
            result = self.handler.scrape_version("1.101")
            
            assert result == False
            
    def test_scrape_all_success(self):
        """Test successful all versions scraping"""
        with patch.object(self.handler, 'get_available_versions_from_main_page') as mock_get:
            with patch.object(self.handler, 'scrape_version') as mock_scrape:
                mock_get.return_value = ["1.101", "1.100", "1.99"]
                mock_scrape.return_value = True
                
                result = self.handler.scrape_all()
                
                assert result == True
                mock_get.assert_called_once()
                assert mock_scrape.call_count == 3
                
    def test_scrape_version_range_success(self):
        """Test successful version range scraping"""
        with patch.object(self.handler, 'get_available_versions_from_main_page') as mock_get:
            with patch.object(self.handler, 'scrape_version') as mock_scrape:
                mock_get.return_value = ["1.101", "1.100", "1.99", "1.98"]
                mock_scrape.return_value = True
                
                result = self.handler.scrape_version_range("1.99", "1.101")
                
                assert result == True
                mock_get.assert_called_once()
                assert mock_scrape.call_count == 3  # 1.99, 1.100, 1.101
                
    def test_save_release_success(self):
        """Test successful release saving"""
        with patch('utils.file_manager.FileManager.save_markdown') as mock_save:
            mock_save.return_value = True
            
            release_data = {
                'version': '1.101',
                'date': 'June 12, 2025',
                'content': 'Release notes content'
            }
            
            result = self.handler.save_release(release_data)
            
            assert result == True
            mock_save.assert_called_once()
            
    def test_network_error_handling(self):
        """Test network error handling"""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = Exception("Connection timeout")
            
            result = self.handler.fetch_page(self.base_url)
            
            assert result is None
            mock_get.assert_called_once_with(self.base_url, timeout=30)
            
    def test_invalid_version_format_handling(self):
        """Test invalid version format handling"""
        result = self.handler.scrape_version("invalid-version")
        assert result == False
        
    def test_version_not_found_handling(self):
        """Test version not found handling"""
        with patch.object(self.handler, 'fetch_page') as mock_fetch:
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_fetch.return_value = mock_response
            
            result = self.handler.scrape_version("999.999")
            
            assert result == False 
