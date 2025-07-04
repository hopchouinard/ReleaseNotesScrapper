import re
import requests
from datetime import datetime
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup

from utils.file_manager import FileManager
from utils.markdown_generator import MarkdownGenerator

class VSCodeHandler:
    """Handles VS Code release notes scraping"""
    
    def __init__(self):
        self.base_url = "https://code.visualstudio.com/updates/"
        self.version_url_pattern = "https://code.visualstudio.com/updates/{version}"
        
    def validate_version_format(self, version: str) -> bool:
        """Validate VS Code version format (e.g., 1.101)"""
        if not version or not isinstance(version, str):
            return False
            
        # Check for format like 1.101, 1.100, etc.
        if not re.match(r'^\d+\.\d+$', version):
            return False
            
        return True
        
    def convert_version_to_url_format(self, version: str) -> str:
        """Convert version to URL format (1.101 -> v1_101)"""
        if not self.validate_version_format(version):
            return version
            
        # Replace dots with underscores and add 'v' prefix
        return f"v{version.replace('.', '_')}"
        
    def build_version_url(self, version: str) -> str:
        """Build URL for specific version"""
        url_version = self.convert_version_to_url_format(version)
        return self.version_url_pattern.format(version=url_version)
        
    def fetch_page(self, url: str) -> Optional[requests.Response]:
        """Fetch page content"""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None
            
    def parse_latest_version_from_main_page(self) -> Optional[str]:
        """Parse latest version from main updates page"""
        response = self.fetch_page(self.base_url)
        if not response:
            return None
            
        try:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for version pattern in headings
            headings = soup.find_all(['h1', 'h2', 'h3'])
            for heading in headings:
                text = heading.get_text()
                # Look for pattern like "May 2025 (version 1.101)"
                match = re.search(r'version (\d+\.\d+)', text, re.IGNORECASE)
                if match:
                    return match.group(1)
                    
            return None
            
        except Exception as e:
            print(f"Error parsing latest version: {e}")
            return None
            
    def parse_version_page_content(self, version: str) -> Optional[Dict[str, Any]]:
        """Parse content from specific version page"""
        url = self.build_version_url(version)
        response = self.fetch_page(url)
        if not response:
            return None
            
        try:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract version and date
            version_info = self.extract_version_info(soup)
            if not version_info:
                return None
                
            # Extract content sections
            sections = self.extract_sections_from_content(soup)
            
            # Combine all content
            content = self.format_content_sections(sections)
            
            return {
                'version': version,
                'date': version_info.get('date', 'Unknown'),
                'content': content
            }
            
        except Exception as e:
            print(f"Error parsing version page: {e}")
            return None
            
    def extract_version_info(self, soup: BeautifulSoup) -> Optional[Dict[str, str]]:
        """Extract version and date information"""
        try:
            # Look for main heading with version
            main_heading = soup.find(['h1', 'h2'])
            if not main_heading:
                return None
            heading_text = main_heading.get_text()
            # Extract version
            version_match = re.search(r'version (\d+\.\d+)', heading_text, re.IGNORECASE)
            if not version_match:
                return None
            version = version_match.group(1)
            # Extract date from heading or nearby <p>
            date_match = re.search(r'Release date: ([^)]+)', heading_text, re.IGNORECASE)
            date = None
            if date_match:
                date = date_match.group(1).strip()
            else:
                # Look for a <p> tag after the heading with 'Release date:'
                p = main_heading.find_next_sibling('p')
                if p:
                    p_text = p.get_text()
                    date_match = re.search(r'Release date: (.+)', p_text, re.IGNORECASE)
                    if date_match:
                        date = date_match.group(1).strip()
            if not date:
                date = 'Unknown'
            return {
                'version': version,
                'date': date
            }
        except Exception as e:
            print(f"Error extracting version info: {e}")
            return None
            
    def extract_sections_from_content(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract content sections from page"""
        sections = {}
        try:
            # Find all h2 headings (section headers)
            h2_elements = soup.find_all('h2')
            for h2 in h2_elements:
                section_name = h2.get_text().strip()
                # Get content until next h2 or end
                content_parts = []
                current = h2.next_sibling
                while current and current.name != 'h2':
                    if getattr(current, 'get_text', None):
                        content_parts.append(current.get_text(separator=' ', strip=True))
                    elif isinstance(current, str) and current.strip():
                        content_parts.append(current.strip())
                    current = current.next_sibling
                if content_parts:
                    sections[section_name] = '\n'.join(content_parts)
        except Exception as e:
            print(f"Error extracting sections: {e}")
        return sections
        
    def format_content_sections(self, sections: Dict[str, str]) -> str:
        """Format sections into readable content"""
        if not sections:
            return ""
            
        content_parts = []
        for section_name, section_content in sections.items():
            content_parts.append(f"## {section_name}\n")
            content_parts.append(section_content)
            content_parts.append("\n")
            
        return '\n'.join(content_parts)
        
    def get_available_versions_from_main_page(self) -> List[str]:
        """Get list of available versions from main page"""
        response = self.fetch_page(self.base_url)
        if not response:
            return []
        try:
            soup = BeautifulSoup(response.text, 'html.parser')
            versions = []
            # Look for links to version pages
            links = soup.find_all('a', href=True)
            for link in links:
                href = link['href']
                # Look for pattern like /updates/v1_101
                match = re.search(r'/updates/v(\d+_\d+)', href)
                if match:
                    version = match.group(1).replace('_', '.')
                    if self.validate_version_format(version):
                        versions.append(version)
            # Remove duplicates and sort numerically
            versions = sorted(set(versions), key=lambda v: [int(x) for x in v.split('.')], reverse=True)
            return versions
        except Exception as e:
            print(f"Error parsing available versions: {e}")
            return []

    def scrape_latest(self) -> bool:
        """Scrape latest version"""
        latest_version = self.parse_latest_version_from_main_page()
        if not latest_version:
            print("Could not determine latest version")
            return False
            
        return self.scrape_version(latest_version)
        
    def scrape_version(self, version: str) -> bool:
        """Scrape specific version"""
        if not self.validate_version_format(version):
            print(f"Invalid version format: {version}")
            return False
            
        release_data = self.parse_version_page_content(version)
        if not release_data:
            return False
            
        return self.save_release(release_data)
        
    def scrape_all(self) -> bool:
        """Scrape all available versions"""
        versions = self.get_available_versions_from_main_page()
        if not versions:
            print("No versions found")
            return False
            
        success_count = 0
        for version in versions:
            if self.scrape_version(version):
                success_count += 1
                
        print(f"Successfully scraped {success_count} out of {len(versions)} versions")
        return success_count > 0
        
    def scrape_version_range(self, from_version: str, to_version: str) -> bool:
        """Scrape releases within a version range (inclusive)"""
        versions = self.get_available_versions_from_main_page()
        if not versions:
            print(f"No versions found in range {from_version} to {to_version}")
            return False
        try:
            # Ensure from_version and to_version are in the list
            if from_version not in versions or to_version not in versions:
                print(f"Version range {from_version} to {to_version} not found in available versions.")
                return False
            from_idx = versions.index(from_version)
            to_idx = versions.index(to_version)
            if from_idx > to_idx:
                selected_versions = versions[to_idx:from_idx+1]
            else:
                selected_versions = versions[from_idx:to_idx+1]
            for version in selected_versions:
                self.scrape_version(version)
            return True
        except Exception as e:
            print(f"Error scraping version range: {e}")
            return False
        
    def save_release(self, release_data: Dict[str, Any]) -> bool:
        """Save release data to markdown file"""
        try:
            file_manager = FileManager()
            markdown_generator = MarkdownGenerator()
            
            # Generate markdown content
            markdown_content = markdown_generator.generate_vscode_release_markdown(release_data)
            
            # Get file path
            file_path = file_manager.get_vscode_file_path(release_data['version'])
            
            # Save file
            if file_manager.save_markdown(file_path, markdown_content):
                print(f"Saved VS Code release {release_data['version']} to {file_path}")
                return True
            else:
                print(f"Failed to save VS Code release {release_data['version']}")
                return False
                
        except Exception as e:
            print(f"Error saving VS Code release: {e}")
            return False 
