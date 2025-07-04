#!/usr/bin/env python3
"""
Release Notes Scraper CLI Application

A command-line tool for scraping release notes from multiple sources
and storing them as organized markdown files.
"""

import click
import os
import re
from datetime import datetime
from typing import Optional

from handlers.github_handler import GitHubHandler
from handlers.vscode_handler import VSCodeHandler
from handlers.web_handler import WebHandler
from utils.config_manager import ConfigManager

def validate_github_repo(ctx, param, value):
    """Validate GitHub repository format"""
    if not value:
        return value
    if not re.match(r'^[a-zA-Z0-9._-]+/[a-zA-Z0-9._-]+$', value):
        raise click.BadParameter('Repository must be in format owner/repo')
    return value

def validate_vscode_version(ctx, param, value):
    """Validate VS Code version format"""
    if not value:
        return value
    if not re.match(r'^\d+\.\d+$', value):
        raise click.BadParameter('Version must be in format X.Y (e.g., 1.101)')
    return value

def validate_url(ctx, param, value):
    """Validate URL format"""
    if not value:
        return value
    if not value.startswith(('http://', 'https://')):
        raise click.BadParameter('URL must start with http:// or https://')
    return value

def validate_date(ctx, param, value):
    """Validate date format"""
    if not value:
        return value
    try:
        datetime.strptime(value, '%Y-%m-%d')
    except ValueError:
        raise click.BadParameter('Date must be in format YYYY-MM-DD')
    return value

@click.group()
@click.version_option(version='1.0.0')
def cli():
    """Release Notes Scraper - Scrape release notes from multiple sources"""
    pass

@cli.command()
@click.option('--repo', required=True, help='Repository name (owner/repo)', callback=validate_github_repo)
@click.option('--latest', is_flag=True, help='Scrape latest release')
@click.option('--version', help='Specific release version/tag')
@click.option('--all', 'all_releases', is_flag=True, help='Scrape all releases')
@click.option('--from', 'from_date', help='Start date (YYYY-MM-DD)', callback=validate_date)
@click.option('--to', 'to_date', help='End date (YYYY-MM-DD)', callback=validate_date)
@click.option('--token', envvar='GITHUB_TOKEN', help='GitHub API token')
def github(repo, latest, version, all_releases, from_date, to_date, token):
    """GitHub repository release notes scraping"""
    handler = GitHubHandler(token=token)
    
    if latest:
        if handler.scrape_latest(repo):
            click.echo(f"Successfully scraped latest release from {repo}")
        else:
            click.echo(f"Failed to scrape latest release from {repo}")
            exit(1)
    elif version:
        if handler.scrape_version(repo, version):
            click.echo(f"Successfully scraped version {version} from {repo}")
        else:
            click.echo(f"Failed to scrape version {version} from {repo}")
            exit(1)
    elif all_releases:
        if handler.scrape_all(repo):
            click.echo(f"Successfully scraped all releases from {repo}")
        else:
            click.echo(f"Failed to scrape releases from {repo}")
            exit(1)
    elif from_date and to_date:
        if handler.scrape_date_range(repo, from_date, to_date):
            click.echo(f"Successfully scraped releases from {repo} between {from_date} and {to_date}")
        else:
            click.echo(f"Failed to scrape releases from {repo}")
            exit(1)
    else:
        click.echo("Please specify one of: --latest, --version, --all, or --from/--to")
        exit(1)

@cli.command()
@click.option('--latest', is_flag=True, help='Scrape latest VS Code release')
@click.option('--version', help='Specific VS Code version (e.g., 1.101)', callback=validate_vscode_version)
@click.option('--all', 'all_versions', is_flag=True, help='Scrape all available VS Code versions')
@click.option('--from', 'from_version', help='Start version (e.g., 1.100)', callback=validate_vscode_version)
@click.option('--to', 'to_version', help='End version (e.g., 1.101)', callback=validate_vscode_version)
def vscode(latest, version, all_versions, from_version, to_version):
    """VS Code release notes scraping"""
    handler = VSCodeHandler()
    
    if latest:
        if handler.scrape_latest():
            click.echo("Successfully scraped latest VS Code release")
        else:
            click.echo("Failed to scrape latest VS Code release")
            exit(1)
    elif version:
        if handler.scrape_version(version):
            click.echo(f"Successfully scraped VS Code version {version}")
        else:
            click.echo(f"Failed to scrape VS Code version {version}")
            exit(1)
    elif all_versions:
        if handler.scrape_all():
            click.echo("Successfully scraped all VS Code versions")
        else:
            click.echo("Failed to scrape VS Code versions")
            exit(1)
    elif from_version and to_version:
        if handler.scrape_version_range(from_version, to_version):
            click.echo(f"Successfully scraped VS Code versions from {from_version} to {to_version}")
        else:
            click.echo(f"Failed to scrape VS Code versions from {from_version} to {to_version}")
            exit(1)
    else:
        click.echo("Please specify one of: --latest, --version, --all, or --from/--to")
        exit(1)

@cli.command()
@click.option('--url', required=True, help='URL to scrape', callback=validate_url)
@click.option('--name', help='Custom source name')
def web(url, name):
    """Generic web page scraping"""
    handler = WebHandler()
    if handler.scrape_url(url, name):
        click.echo(f"Successfully scraped release notes from {url}")
    else:
        click.echo(f"Failed to scrape release notes from {url}")
        exit(1)

if __name__ == '__main__':
    cli() 
