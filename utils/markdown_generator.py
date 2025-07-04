from datetime import datetime
from typing import Dict, Any, List
import re
from bs4 import BeautifulSoup

class MarkdownGenerator:
    """Generates markdown content from release data"""
    
    def __init__(self):
        pass
        
    def generate_github_release_markdown(self, repo_name: str, release_data: Dict[str, Any]) -> str:
        """Generate markdown for GitHub release"""
        version = release_data.get('version', 'Unknown')
        date = release_data.get('date', 'Unknown')
        content = release_data.get('content', '')
        author = release_data.get('author', 'Unknown')
        assets = release_data.get('assets', [])
        
        # Format date
        if isinstance(date, datetime):
            date_str = date.strftime('%Y-%m-%d')
        else:
            date_str = str(date)
            
        markdown = f"# {repo_name} - {version}\n\n"
        markdown += f"**Release Date**: {date_str}\n"
        markdown += f"**Author**: {author}\n"
        markdown += f"**Source**: https://github.com/{repo_name}/releases/tag/{version}\n"
        markdown += f"**Scraped**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        if content:
            markdown += "## Overview\n\n"
            markdown += self.clean_markdown_content(content)
            markdown += "\n\n"
            
        if assets:
            markdown += "## Downloads\n\n"
            for asset in assets:
                if isinstance(asset, dict):
                    name = asset.get('name', 'Unknown')
                    url = asset.get('url', '#')
                    markdown += f"- [{name}]({url})\n"
                else:
                    markdown += f"- {asset}\n"
            markdown += "\n"
            
        markdown += f"---\n*Scraped from https://github.com/{repo_name}/releases/tag/{version} on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
        
        return markdown
        
    def generate_vscode_release_markdown(self, release_data: Dict[str, Any]) -> str:
        """Generate markdown for VS Code release"""
        version = release_data.get('version', 'Unknown')
        date = release_data.get('date', 'Unknown')
        content = release_data.get('content', '')
        
        # Convert version to URL format
        url_version = version.replace('.', '_')
        source_url = f"https://code.visualstudio.com/updates/v{url_version}"
        
        markdown = f"# Visual Studio Code - {version}\n\n"
        markdown += f"**Release Date**: {date}\n"
        markdown += f"**Source**: {source_url}\n"
        markdown += f"**Scraped**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        if content:
            markdown += "## Changes\n\n"
            markdown += self.clean_markdown_content(content)
            markdown += "\n\n"
            
        markdown += f"---\n*Scraped from {source_url} on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
        
        return markdown
        
    def generate_web_release_markdown(self, source_name: str, release_data: Dict[str, Any], source_url: str) -> str:
        """Generate markdown for web release"""
        title = release_data.get('title', 'Unknown Release')
        date = release_data.get('date', 'Unknown')
        content = release_data.get('content', '')
        
        markdown = f"# {source_name} - {title}\n\n"
        markdown += f"**Release Date**: {date}\n"
        markdown += f"**Source**: {source_url}\n"
        markdown += f"**Scraped**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        if content:
            markdown += "## Changes\n\n"
            markdown += self.clean_markdown_content(content)
            markdown += "\n\n"
            
        markdown += f"---\n*Scraped from {source_url} on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
        
        return markdown
        
    def format_content_sections(self, sections: Dict[str, str]) -> str:
        """Format content sections into markdown"""
        markdown = ""
        for section_name, section_content in sections.items():
            markdown += f"## {section_name}\n\n"
            markdown += self.clean_markdown_content(section_content)
            markdown += "\n\n"
        return markdown
        
    def clean_markdown_content(self, content: str) -> str:
        """Clean and convert HTML content to markdown"""
        if not content:
            return ""
            
        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')
        
        # Remove script and style tags
        for script in soup(["script", "style", "noscript"]):
            script.decompose()
            
        # Convert common HTML tags to markdown
        text = str(soup)
        
        # Convert headings
        text = re.sub(r'<h1[^>]*>(.*?)</h1>', r'# \1', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'<h2[^>]*>(.*?)</h2>', r'## \1', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'<h3[^>]*>(.*?)</h3>', r'### \1', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'<h4[^>]*>(.*?)</h4>', r'#### \1', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'<h5[^>]*>(.*?)</h5>', r'##### \1', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'<h6[^>]*>(.*?)</h6>', r'###### \1', text, flags=re.IGNORECASE | re.DOTALL)
        
        # Convert paragraphs
        text = re.sub(r'<p[^>]*>(.*?)</p>', r'\1\n\n', text, flags=re.IGNORECASE | re.DOTALL)
        
        # Convert lists
        text = re.sub(r'<ul[^>]*>(.*?)</ul>', r'\1', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'<ol[^>]*>(.*?)</ol>', r'\1', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'<li[^>]*>(.*?)</li>', r'- \1\n', text, flags=re.IGNORECASE | re.DOTALL)
        
        # Convert emphasis
        text = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'<b[^>]*>(.*?)</b>', r'**\1**', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'<em[^>]*>(.*?)</em>', r'*\1*', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'<i[^>]*>(.*?)</i>', r'*\1*', text, flags=re.IGNORECASE | re.DOTALL)
        
        # Convert links
        text = re.sub(r'<a[^>]*href=["\']([^"\']*)["\'][^>]*>(.*?)</a>', r'[\2](\1)', text, flags=re.IGNORECASE | re.DOTALL)
        
        # Convert code
        text = re.sub(r'<code[^>]*>(.*?)</code>', r'`\1`', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'<pre[^>]*>(.*?)</pre>', r'```\n\1\n```', text, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove remaining HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Clean up whitespace
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
        text = text.strip()
        
        return text
        
    def add_metadata(self, content: str, metadata: Dict[str, Any]) -> str:
        """Add metadata to markdown content"""
        if not metadata:
            return content
            
        metadata_lines = []
        for key, value in metadata.items():
            if key == 'source':
                metadata_lines.append(f"**Source**: {value}")
            elif key == 'scraped':
                if isinstance(value, datetime):
                    metadata_lines.append(f"**Scraped**: {value.strftime('%Y-%m-%d %H:%M:%S')}")
                else:
                    metadata_lines.append(f"**Scraped**: {value}")
                    
        if metadata_lines:
            content += "\n\n" + "\n".join(metadata_lines)
            
        # Add footer
        source = metadata.get('source', 'Unknown')
        scraped = metadata.get('scraped', datetime.now())
        if isinstance(scraped, datetime):
            scraped_str = scraped.strftime('%Y-%m-%d %H:%M:%S')
        else:
            scraped_str = str(scraped)
            
        content += f"\n\n---\n*Scraped from {source} on {scraped_str}*"
        
        return content 
