import re
import requests
from urllib.parse import urlparse
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup

from utils.file_manager import FileManager
from utils.markdown_generator import MarkdownGenerator

class WebHandler:
    """Handles generic web page release notes scraping"""
    
    def __init__(self):
        self.file_manager = FileManager()
        self.markdown_generator = MarkdownGenerator()
        
    def validate_url_format(self, url: str) -> bool:
        """Validate URL format"""
        if not url or not isinstance(url, str):
            return False
        try:
            parsed = urlparse(url)
            return bool(parsed.scheme in ['http', 'https'] and parsed.netloc)
        except:
            return False
            
    def extract_name_from_url(self, url: str) -> str:
        """Extract domain name from URL"""
        try:
            parsed = urlparse(url)
            return parsed.netloc
        except:
            return "unknown"
            
    def fetch_page(self, url: str) -> Optional[requests.Response]:
        """Fetch page content"""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None
            
    def parse_page_content(self, url: str) -> Optional[Dict[str, Any]]:
        """Parse content from web page"""
        response = self.fetch_page(url)
        if not response:
            return None
            
        try:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title
            title = self.extract_title_from_content(soup)
            
            # Extract date
            date = self.extract_date_from_content(soup)
            
            # Extract main content
            content = self.extract_main_content(soup)
            
            return {
                'title': title,
                'date': date,
                'content': content,
                'url': url
            }
            
        except Exception as e:
            print(f"Error parsing page content: {e}")
            return None
            
    def extract_title_from_content(self, soup: BeautifulSoup) -> str:
        """Extract title from content"""
        # Try to find h1 first
        h1 = soup.find('h1')
        if h1:
            return h1.get_text().strip()
            
        # Fallback to page title
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text().strip()
            
        return "Unknown Title"
        
    def extract_date_from_content(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract date from content"""
        # Look for common date patterns
        date_patterns = [
            r'Release date:\s*([^<\n]+)',
            r'Published:\s*([^<\n]+)',
            r'Date:\s*([^<\n]+)',
            r'(\w+ \d{1,2}, \d{4})',
            r'(\d{4}-\d{2}-\d{2})'
        ]
        
        text = soup.get_text()
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
                
        return None
        
    def extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main content from page"""
        # Try to find main content areas
        content_selectors = [
            'main',
            '.content',
            '#content',
            '.main-content',
            'article',
            '.post-content'
        ]
        
        for selector in content_selectors:
            content = soup.select_one(selector)
            if content:
                return self.clean_content(str(content))
                
        # Fallback to body content
        body = soup.find('body')
        if body:
            return self.clean_content(str(body))
            
        return ""
        
    def clean_content(self, content: str) -> str:
        """Clean HTML content"""
        # Remove script and style tags
        soup = BeautifulSoup(content, 'html.parser')
        
        # Remove unwanted tags
        for tag in soup(['script', 'style', 'noscript', 'nav', 'header', 'footer']):
            tag.decompose()
            
        # Get clean text
        text = soup.get_text(separator='\n', strip=True)
        
        # Clean up whitespace
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        return '\n'.join(lines)
        
    def scrape_url(self, url: str, name: Optional[str] = None) -> bool:
        """Scrape release notes from URL"""
        if not self.validate_url_format(url):
            print(f"Invalid URL format: {url}")
            return False
            
        # Parse page content
        release_data = self.parse_page_content(url)
        if not release_data:
            print(f"Failed to parse content from {url}")
            return False
            
        # Extract name if not provided
        if not name:
            name = self.extract_name_from_url(url)
            
        # Save release
        return self.save_release(release_data, name)
        
    def save_release(self, release_data: Dict[str, Any], name: str) -> bool:
        """Save release data to file"""
        try:
            # Handle None name
            if name is None:
                name = "unknown"
                
            # Generate markdown content
            markdown = self.markdown_generator.generate_web_release_markdown(
                name, release_data, release_data.get('url', '')
            )
            
            # Generate filename from title or use default
            title = release_data.get('title', 'release')
            filename = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_').lower()
            if not filename:
                filename = 'release'
                
            # Save to file
            file_path = self.file_manager.get_web_file_path(name, filename)
            return self.file_manager.save_markdown(file_path, markdown)
            
        except Exception as e:
            print(f"Error saving release: {e}")
            return False 
