# Release Notes Scraper

A powerful command-line tool for scraping release notes from multiple sources and storing them as organized markdown files. Perfect for developers, DevOps teams, and anyone who needs to track software releases across different platforms.

## 🚀 Features

- **Multi-Source Support**: Scrape from GitHub repositories, VS Code releases, and generic web pages
- **Organized Storage**: Automatically organizes release notes in a hierarchical file structure
- **Flexible Output**: Generates clean, formatted markdown files with metadata
- **Error Handling**: Robust error handling with graceful fallbacks
- **Rate Limiting**: Respects API limits and implements proper rate limiting
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Extensible**: Easy to add new sources with the modular architecture

## 📋 Requirements

- Python 3.8 or higher
- Internet connection for scraping
- Git (for cloning the repository)

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd ReleaseNotesScrapper
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

### 3. Activate the Virtual Environment

**Windows:**

```bash
.venv\Scripts\activate
```

**macOS/Linux:**

```bash
source .venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

## 📖 Usage Guide

### Basic Command Structure

```bash
python scraper.py <source> [options]
```

### GitHub Repository Scraping

#### Scrape Latest Release

```bash
python scraper.py github --repo microsoft/vscode --latest
```

#### Scrape Specific Version

```bash
python scraper.py github --repo microsoft/vscode --version v1.101.0
```

#### Scrape All Releases

```bash
python scraper.py github --repo microsoft/vscode --all
```

#### Scrape Releases in Date Range

```bash
python scraper.py github --repo microsoft/vscode --from 2024-01-01 --to 2024-12-31
```

#### Using GitHub Token (Optional)

```bash
python scraper.py github --repo microsoft/vscode --latest --token YOUR_GITHUB_TOKEN
```

Or set environment variable:

```bash
export GITHUB_TOKEN=your_token_here
python scraper.py github --repo microsoft/vscode --latest
```

### VS Code Release Scraping

#### Scrape Latest VS Code Release

```bash
python scraper.py vscode --latest
```

#### Scrape Specific Version

```bash
python scraper.py vscode --version 1.101
```

#### Scrape All Available Versions

```bash
python scraper.py vscode --all
```

#### Scrape Version Range

```bash
python scraper.py vscode --from 1.100 --to 1.101
```

### Generic Web Page Scraping

#### Scrape Specific URL

```bash
python scraper.py web --url https://example.com/releases/v1.0.0
```

#### Scrape with Custom Name

```bash
python scraper.py web --url https://example.com/releases/v1.0.0 --name my-app
```

## 📁 Output Structure

The application creates an organized directory structure for storing release notes:

```plaintext
releases/
├── github/
│   └── {owner}/
│       └── {repo}/
│           ├── v1.101.0.md
│           ├── v1.100.0.md
│           └── ...
├── vscode/
│   ├── 1.101.md
│   ├── 1.100.md
│   └── ...
└── other-sources/
    └── {source-name}/
        ├── release_v1.0.0.md
        └── ...
```

## 📄 Output Format

Each release note is saved as a markdown file with the following structure:

### GitHub Release Example

```markdown
# microsoft/vscode - v1.101.0

**Release Date**: 2024-01-15  
**Source**: https://github.com/microsoft/vscode/releases/tag/v1.101.0  
**Scraped**: 2024-01-15 10:30:00

## Overview
Latest release with new features and bug fixes.

## Changes
- New feature A
- Bug fix B
- Performance improvements

## Downloads
- [vscode-windows-x64-1.101.0.exe](https://github.com/microsoft/vscode/releases/download/v1.101.0/VSCodeUserSetup-x64-1.101.0.exe)

## Contributors
- @username1
- @username2

---
*Scraped from https://github.com/microsoft/vscode/releases/tag/v1.101.0 on 2024-01-15 10:30:00*
```

### VS Code Release Example

```markdown
# Visual Studio Code - 1.101

**Release Date**: June 12, 2025  
**Source**: https://code.visualstudio.com/updates/v1_101  
**Scraped**: 2024-01-15 10:30:00

## Chat
Chat improvements and new features.

## Editor Experience
Enhanced editor functionality and performance.

## Notable fixes
- Bug fix 1
- Bug fix 2

---
*Scraped from https://code.visualstudio.com/updates/v1_101 on 2024-01-15 10:30:00*
```

## ⚙️ Configuration

### Environment Variables

- `GITHUB_TOKEN`: GitHub API token for authenticated requests (optional but recommended)

### Configuration Files

The application uses configuration files in the `config/` directory:

```json
{
  "github": {
    "api_base": "https://api.github.com",
    "file_directory": "releases/github",
    "template": "templates/github_template.md",
    "rate_limit": {
      "requests_per_hour": 5000,
      "requests_per_minute": 60
    }
  },
  "vscode": {
    "base_url": "https://code.visualstudio.com/updates/",
    "version_url_pattern": "https://code.visualstudio.com/updates/{version}",
    "file_directory": "releases/vscode",
    "template": "templates/vscode_template.md",
    "version_format": "underscore"
  },
  "web": {
    "file_directory": "releases/other-sources",
    "template": "templates/web_template.md"
  }
}
```

## 🔧 Advanced Usage

### Batch Processing

You can create scripts to scrape multiple repositories:

```bash
#!/bin/bash
# scrape_multiple_repos.sh

repos=("microsoft/vscode" "microsoft/typescript" "facebook/react")

for repo in "${repos[@]}"; do
    echo "Scraping $repo..."
    python scraper.py github --repo "$repo" --latest
done
```

### Integration with CI/CD

Add to your CI/CD pipeline to automatically track releases:

```yaml
# .github/workflows/track-releases.yml
name: Track Releases
on:
  schedule:
    - cron: '0 9 * * *'  # Daily at 9 AM

jobs:
  track-releases:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Track releases
        run: |
          python scraper.py github --repo microsoft/vscode --latest
          python scraper.py vscode --latest
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Rate Limiting (GitHub)

**Error**: `API rate limit exceeded`

**Solution**:

- Use a GitHub token: `python scraper.py github --repo owner/repo --latest --token YOUR_TOKEN`
- Wait for rate limit reset (usually 1 hour)
- Use authenticated requests for higher limits

#### 2. Permission Denied

**Error**: `Permission denied` when creating directories

**Solution**:

- Ensure write permissions in the target directory
- Run with appropriate user permissions
- Check disk space availability

#### 3. Network Issues

**Error**: `Connection timeout` or `Network error`

**Solution**:

- Check internet connection
- Verify target URLs are accessible
- Try again later if service is temporarily unavailable

#### 4. Invalid Repository Format

**Error**: `Repository must be in format owner/repo`

**Solution**:

- Use correct format: `owner/repository-name`
- Avoid special characters in repository names
- Ensure repository exists and is public (or you have access)

#### 5. Version Not Found

**Error**: `Version not found` or `Release not found`

**Solution**:

- Verify version/tag exists
- Check spelling and format
- Use `--all` to see available versions first

### Debug Mode

Enable verbose output for debugging:

```bash
# Set environment variable for debug output
export DEBUG=1
python scraper.py github --repo microsoft/vscode --latest
```

## 🧪 Testing

Run the test suite to ensure everything is working:

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/test_github_handler.py -v
python -m pytest tests/test_vscode_handler.py -v
python -m pytest tests/test_web_handler.py -v
python -m pytest tests/test_cli.py -v
```

## 📊 Performance Tips

1. **Use GitHub Tokens**: Authenticated requests have higher rate limits
2. **Batch Processing**: Group multiple scraping operations
3. **Incremental Updates**: Use `--latest` instead of `--all` for regular updates
4. **Local Caching**: The application automatically skips existing files

## 🔒 Security Considerations

- **GitHub Tokens**: Store tokens securely, never commit them to version control
- **File Permissions**: Ensure proper file permissions for sensitive data
- **Network Security**: Use HTTPS URLs and verify SSL certificates
- **Input Validation**: The application validates all inputs to prevent injection attacks

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Add tests for new functionality
5. Run the test suite: `python -m pytest tests/ -v`
6. Commit your changes: `git commit -am 'Add feature'`
7. Push to the branch: `git push origin feature-name`
8. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- GitHub API for repository data
- VS Code team for release notes
- BeautifulSoup for HTML parsing
- Click for CLI framework
- All contributors and users

## 📞 Support

- **Issues**: Report bugs and feature requests on GitHub Issues
- **Documentation**: Check this README and inline code comments
- **Community**: Join discussions in GitHub Discussions

## 🔄 Version History

- **v1.0.0**: Initial release with GitHub, VS Code, and web scraping support
- **v1.0.1**: Bug fixes and performance improvements
- **v1.1.0**: Added date range filtering and enhanced error handling

---

### **Happy Scraping! 🚀**

For more information, visit the [project repository](https://github.com/yourusername/release-notes-scraper).
