import pytest
from unittest.mock import patch, MagicMock, Mock
import json
import os
from datetime import datetime
from bs4 import BeautifulSoup

from handlers.web_handler import WebHandler

class TestWebHandler:
    """Test suite for web handler"""
    
    def setup_method(self):
        """Setup test environment"""
        self.handler = WebHandler()
        self.mock_url = "https://example.com/releases/v1.0.0"
        self.mock_name = "my-app"
        
    def test_init(self):
        """Test handler initialization"""
        assert self.handler is not None
        
    def test_validate_url_format_valid(self):
        """Test valid URL format validation"""
        assert self.handler.validate_url_format("https://example.com/releases/v1.0.0") == True
        assert self.handler.validate_url_format("http://example.com/releases/v1.0.0") == True
        assert self.handler.validate_url_format("https://code.visualstudio.com/updates/v1_101") == True
        
    def test_validate_url_format_invalid(self):
        """Test invalid URL format validation"""
        assert self.handler.validate_url_format("not-a-url") == False
        assert self.handler.validate_url_format("ftp://example.com") == False
        assert self.handler.validate_url_format("") == False
        assert self.handler.validate_url_format("example.com") == False
        
    def test_extract_name_from_url(self):
        """Test extracting name from URL"""
        assert self.handler.extract_name_from_url("https://example.com/releases/v1.0.0") == "example.com"
        assert self.handler.extract_name_from_url("https://code.visualstudio.com/updates/v1_101") == "code.visualstudio.com"
        assert self.handler.extract_name_from_url("https://github.com/owner/repo/releases/tag/v1.0.0") == "github.com"
        
    def test_fetch_page_success(self):
        """Test successful page fetching"""
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = "<html><body>Test content</body></html>"
            mock_get.return_value = mock_response
            
            result = self.handler.fetch_page(self.mock_url)
            
            assert result is not None
            assert result.status_code == 200
            mock_get.assert_called_once_with(self.mock_url, timeout=30)
            
    def test_fetch_page_failure(self):
        """Test page fetching failure"""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = Exception("Network error")
            
            result = self.handler.fetch_page(self.mock_url)
            assert result is None
            
    def test_parse_page_content_success(self):
        """Test successful page content parsing"""
        html_content = """
        <html>
        <head>
            <title>Release v1.0.0</title>
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
                <h2>Bug Fixes</h2>
                <ul>
                    <li>Bug fix 1</li>
                    <li>Bug fix 2</li>
                </ul>
            </div>
        </body>
        </html>
        """
        
        with patch.object(self.handler, 'fetch_page') as mock_fetch:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = html_content
            mock_fetch.return_value = mock_response
            
            result = self.handler.parse_page_content(self.mock_url)
            
            assert result is not None
            assert result['title'] == "Release v1.0.0"
            assert result['date'] == "January 1, 2024"
            assert 'Features' in result['content']
            assert 'Bug Fixes' in result['content']
            assert 'New feature 1' in result['content']
            assert 'Bug fix 1' in result['content']
            
    def test_parse_page_content_not_found(self):
        """Test page content parsing when not found"""
        with patch.object(self.handler, 'fetch_page') as mock_fetch:
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_fetch.return_value = mock_response
            
            result = self.handler.parse_page_content(self.mock_url)
            
            assert result is None
            
    def test_extract_title_from_content(self):
        """Test extracting title from content"""
        html_content = """
        <html>
        <head>
            <title>Release v1.0.0 - My App</title>
        </head>
        <body>
            <h1>Release v1.0.0</h1>
            <h2>Another heading</h2>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(html_content, 'html.parser')
        title = self.handler.extract_title_from_content(soup)
        
        assert title == "Release v1.0.0"
        
    def test_extract_title_fallback(self):
        """Test title extraction fallback"""
        html_content = """
        <html>
        <head>
            <title>Release v1.0.0 - My App</title>
        </head>
        <body>
            <h2>Another heading</h2>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(html_content, 'html.parser')
        title = self.handler.extract_title_from_content(soup)
        
        assert title == "Release v1.0.0 - My App"
        
    def test_extract_date_from_content(self):
        """Test extracting date from content"""
        html_content = """
        <html>
        <body>
            <p>Release date: January 1, 2024</p>
            <p>Published: December 31, 2023</p>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(html_content, 'html.parser')
        date = self.handler.extract_date_from_content(soup)
        
        assert date == "January 1, 2024"
        
    def test_extract_date_not_found(self):
        """Test date extraction when not found"""
        html_content = """
        <html>
        <body>
            <p>No date information</p>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(html_content, 'html.parser')
        date = self.handler.extract_date_from_content(soup)
        
        assert date is None
        
    def test_extract_main_content(self):
        """Test extracting main content"""
        html_content = """
        <html>
        <body>
            <header>Header content</header>
            <main>
                <h2>Features</h2>
                <ul>
                    <li>Feature 1</li>
                    <li>Feature 2</li>
                </ul>
                <h2>Bug Fixes</h2>
                <ul>
                    <li>Bug fix 1</li>
                </ul>
            </main>
            <footer>Footer content</footer>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(html_content, 'html.parser')
        content = self.handler.extract_main_content(soup)
        
        assert 'Features' in content
        assert 'Bug Fixes' in content
        assert 'Feature 1' in content
        assert 'Bug fix 1' in content
        assert 'Header content' not in content
        assert 'Footer content' not in content
        
    def test_clean_content(self):
        """Test content cleaning"""
        dirty_content = """
        <script>alert('test');</script>
        <style>.hidden { display: none; }</style>
        <div class="content">
            <h2>Features</h2>
            <p>This is <strong>important</strong> content.</p>
            <ul>
                <li>Feature 1</li>
                <li>Feature 2</li>
            </ul>
        </div>
        <noscript>No script content</noscript>
        """
        
        cleaned = self.handler.clean_content(dirty_content)
        
        assert 'script' not in cleaned.lower()
        assert 'style' not in cleaned.lower()
        assert 'noscript' not in cleaned.lower()
        assert 'Features' in cleaned
        assert 'important' in cleaned
        assert 'Feature 1' in cleaned
        
    def test_scrape_url_success(self):
        """Test successful URL scraping"""
        with patch.object(self.handler, 'parse_page_content') as mock_parse:
            with patch.object(self.handler, 'save_release') as mock_save:
                mock_parse.return_value = {
                    'title': 'Release v1.0.0',
                    'date': 'January 1, 2024',
                    'content': 'Release notes content'
                }
                mock_save.return_value = True
                
                result = self.handler.scrape_url(self.mock_url, self.mock_name)
                
                assert result == True
                mock_parse.assert_called_once_with(self.mock_url)
                mock_save.assert_called_once()
                
    def test_scrape_url_without_name(self):
        """Test URL scraping without custom name"""
        with patch.object(self.handler, 'parse_page_content') as mock_parse:
            with patch.object(self.handler, 'save_release') as mock_save:
                mock_parse.return_value = {
                    'title': 'Release v1.0.0',
                    'date': 'January 1, 2024',
                    'content': 'Release notes content'
                }
                mock_save.return_value = True
                
                result = self.handler.scrape_url(self.mock_url, None)
                
                assert result == True
                mock_parse.assert_called_once_with(self.mock_url)
                mock_save.assert_called_once()
                
    def test_scrape_url_failure(self):
        """Test URL scraping failure"""
        with patch.object(self.handler, 'parse_page_content') as mock_parse:
            mock_parse.return_value = None
            
            result = self.handler.scrape_url(self.mock_url, self.mock_name)
            
            assert result == False
            
    def test_save_release_success(self):
        """Test successful release saving"""
        with patch('utils.file_manager.FileManager.save_markdown') as mock_save:
            mock_save.return_value = True
            
            release_data = {
                'title': 'Release v1.0.0',
                'date': 'January 1, 2024',
                'content': 'Release notes content'
            }
            
            result = self.handler.save_release(release_data, self.mock_name)
            
            assert result == True
            mock_save.assert_called_once()
            
    def test_save_release_with_extracted_name(self):
        """Test release saving with extracted name"""
        with patch('utils.file_manager.FileManager.save_markdown') as mock_save:
            mock_save.return_value = True
            
            release_data = {
                'title': 'Release v1.0.0',
                'date': 'January 1, 2024',
                'content': 'Release notes content'
            }
            
            result = self.handler.save_release(release_data, None)
            
            assert result == True
            mock_save.assert_called_once()
            
    def test_network_error_handling(self):
        """Test network error handling"""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = Exception("Connection timeout")
            
            result = self.handler.fetch_page(self.mock_url)
            
            assert result is None
            
    def test_invalid_url_format_handling(self):
        """Test invalid URL format handling"""
        result = self.handler.scrape_url("not-a-url", self.mock_name)
        assert result == False
        
    def test_url_not_found_handling(self):
        """Test URL not found handling"""
        with patch.object(self.handler, 'fetch_page') as mock_fetch:
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_fetch.return_value = mock_response
            
            result = self.handler.scrape_url("https://example.com/not-found", self.mock_name)
            
            assert result == False
            
    def test_content_parsing_error_handling(self):
        """Test content parsing error handling"""
        with patch.object(self.handler, 'fetch_page') as mock_fetch:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = "Invalid HTML content"
            mock_fetch.return_value = mock_response
            
            result = self.handler.parse_page_content(self.mock_url)
            
            # Should handle invalid HTML gracefully
            assert result is not None 
