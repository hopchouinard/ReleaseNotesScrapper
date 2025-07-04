import os
import re
from typing import Optional

class FileManager:
    """Manages file operations and directory structure"""
    
    def __init__(self, base_dir: str = "."):
        self.base_dir = base_dir
        
    def create_directory(self, directory_path: str) -> bool:
        """Create directory if it doesn't exist. Return False on any error."""
        try:
            os.makedirs(directory_path, exist_ok=True)
            # Check if directory was actually created
            return os.path.isdir(directory_path)
        except Exception as e:
            print(f"Error creating directory {directory_path}: {e}")
            return False
            
    def save_markdown(self, file_path: str, content: str) -> bool:
        """Save markdown content to file. Return False on any error."""
        try:
            directory = os.path.dirname(file_path)
            if directory and not self.create_directory(directory):
                return False
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error saving file {file_path}: {e}")
            return False
            
    def file_exists(self, file_path: str) -> bool:
        """Check if file exists"""
        return os.path.exists(file_path)
        
    def get_file_path(self, source_type: str, project_name: str, version: str) -> str:
        """Generate file path for release notes"""
        # Split project name for nested directory structure, then clean each part
        project_parts = [self.clean_filename(part) for part in project_name.split('/')]
        project_dir = os.path.join(*project_parts)
        # Clean version for filename
        clean_version = self.clean_filename(version)
        # Build file path
        file_path = os.path.join(
            self.base_dir,
            "releases",
            source_type,
            project_dir,
            f"{clean_version}.md"
        )
        return file_path
        
    def clean_filename(self, filename: str) -> str:
        """Clean filename to be filesystem-safe"""
        # Replace invalid characters with underscores
        cleaned = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Remove leading/trailing spaces and dots
        cleaned = cleaned.strip('. ')
        # Replace multiple underscores with single
        cleaned = re.sub(r'_+', '_', cleaned)
        return cleaned
        
    def get_vscode_file_path(self, version: str) -> str:
        """Generate file path for VS Code release notes"""
        clean_version = self.clean_filename(version)
        file_path = os.path.join(
            self.base_dir,
            "releases",
            "vscode",
            f"{clean_version}.md"
        )
        return file_path
        
    def get_web_file_path(self, source_name: str, identifier: str) -> str:
        """Generate file path for web release notes"""
        clean_source = self.clean_filename(source_name)
        clean_identifier = self.clean_filename(identifier)
        file_path = os.path.join(
            self.base_dir,
            "releases",
            "other-sources",
            clean_source,
            f"{clean_identifier}.md"
        )
        return file_path 
