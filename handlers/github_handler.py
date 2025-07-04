import re
from datetime import datetime
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse

from utils.file_manager import FileManager
from utils.markdown_generator import MarkdownGenerator

try:
    from github import Github
except ImportError:
    Github = None

class GitHubHandler:
    """Handles GitHub API interactions and release scraping"""
    
    def __init__(self, token: Optional[str] = None):
        self.github = None
        self.repo = None
        self.repo_name = None
        
        if token and Github:
            try:
                self.github = Github(token)
            except Exception as e:
                print(f"Error initializing GitHub client: {e}")
                
    def validate_repo_format(self, repo: str) -> bool:
        """Validate repository format (owner/repo)"""
        if not repo or not isinstance(repo, str):
            return False
            
        # Check for owner/repo format
        parts = repo.split('/')
        if len(parts) != 2:
            return False
            
        owner, repo_name = parts
        if not owner or not repo_name:
            return False
            
        # Check for valid characters
        if not re.match(r'^[a-zA-Z0-9._-]+$', owner) or not re.match(r'^[a-zA-Z0-9._-]+$', repo_name):
            return False
            
        return True
        
    def setup_repo(self, repo: str) -> bool:
        """Setup repository for operations"""
        if not self.validate_repo_format(repo):
            print(f"Invalid repository format: {repo}")
            return False
            
        if not self.github:
            print("GitHub client not initialized. Please provide a valid token.")
            return False
            
        try:
            self.repo = self.github.get_repo(repo)
            self.repo_name = repo
            return True
        except Exception as e:
            print(f"Error accessing repository {repo}: {e}")
            return False
            
    def get_latest_release(self, repo: str) -> Optional[Dict[str, Any]]:
        """Get latest release from repository"""
        if not self.setup_repo(repo):
            return None
            
        try:
            release = self.repo.get_latest_release()
            return {
                'version': release.tag_name,
                'date': release.published_at,
                'content': release.body or '',
                'author': release.author.login if release.author else 'Unknown',
                'assets': [{'name': asset.name, 'url': asset.browser_download_url} for asset in release.assets]
            }
        except Exception as e:
            print(f"Error getting latest release: {e}")
            return None
            
    def get_release_by_version(self, repo: str, version: str) -> Optional[Dict[str, Any]]:
        """Get specific release by version"""
        if not self.setup_repo(repo):
            return None
            
        try:
            release = self.repo.get_release(version)
            return {
                'version': release.tag_name,
                'date': release.published_at,
                'content': release.body or '',
                'author': release.author.login if release.author else 'Unknown',
                'assets': [{'name': asset.name, 'url': asset.browser_download_url} for asset in release.assets]
            }
        except Exception as e:
            print(f"Error getting release {version}: {e}")
            return None
            
    def get_all_releases(self, repo: str) -> List[Dict[str, Any]]:
        """Get all releases from repository"""
        if not self.setup_repo(repo):
            return []
            
        try:
            releases = self.repo.get_releases()
            result = []
            for release in releases:
                result.append({
                    'version': release.tag_name,
                    'date': release.published_at,
                    'content': release.body or '',
                    'author': release.author.login if release.author else 'Unknown',
                    'assets': [{'name': asset.name, 'url': asset.browser_download_url} for asset in release.assets]
                })
            return result
        except Exception as e:
            print(f"Error getting all releases: {e}")
            return []
            
    def get_releases_by_date_range(self, repo: str, from_date: str, to_date: str) -> List[Dict[str, Any]]:
        """Get releases within a date range"""
        if not self.setup_repo(repo):
            return []
            
        try:
            from_dt = datetime.strptime(from_date, '%Y-%m-%d')
            to_dt = datetime.strptime(to_date, '%Y-%m-%d')
            
            releases = self.repo.get_releases()
            result = []
            for release in releases:
                if release.published_at and from_dt <= release.published_at <= to_dt:
                    result.append({
                        'version': release.tag_name,
                        'date': release.published_at,
                        'content': release.body or '',
                        'author': release.author.login if release.author else 'Unknown',
                        'assets': [{'name': asset.name, 'url': asset.browser_download_url} for asset in release.assets]
                    })
            return result
        except Exception as e:
            print(f"Error getting releases by date range: {e}")
            return []
            
    def scrape_latest(self, repo: str) -> bool:
        """Scrape latest release and save to file"""
        release_data = self.get_latest_release(repo)
        if not release_data:
            return False
            
        return self.save_release(repo, release_data)
        
    def scrape_version(self, repo: str, version: str) -> bool:
        """Scrape specific version and save to file"""
        release_data = self.get_release_by_version(repo, version)
        if not release_data:
            return False
            
        return self.save_release(repo, release_data)
        
    def scrape_all(self, repo: str) -> bool:
        """Scrape all releases and save to files"""
        releases = self.get_all_releases(repo)
        if not releases:
            return False
            
        success_count = 0
        for release_data in releases:
            if self.save_release(repo, release_data):
                success_count += 1
                
        print(f"Successfully scraped {success_count} out of {len(releases)} releases")
        return success_count > 0
        
    def scrape_date_range(self, repo: str, from_date: str, to_date: str) -> bool:
        """Scrape releases within date range and save to files"""
        releases = self.get_releases_by_date_range(repo, from_date, to_date)
        if not releases:
            return False
            
        success_count = 0
        for release_data in releases:
            if self.save_release(repo, release_data):
                success_count += 1
                
        print(f"Successfully scraped {success_count} out of {len(releases)} releases")
        return success_count > 0
        
    def save_release(self, repo: str, release_data: Dict[str, Any]) -> bool:
        """Save release data to markdown file"""
        try:
            file_manager = FileManager()
            markdown_generator = MarkdownGenerator()
            
            # Generate markdown content
            markdown_content = markdown_generator.generate_github_release_markdown(repo, release_data)
            
            # Get file path
            file_path = file_manager.get_file_path("github", repo, release_data['version'])
            
            # Save file
            if file_manager.save_markdown(file_path, markdown_content):
                print(f"Saved release {release_data['version']} to {file_path}")
                return True
            else:
                print(f"Failed to save release {release_data['version']}")
                return False
                
        except Exception as e:
            print(f"Error saving release: {e}")
            return False 
