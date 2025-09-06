#!/usr/bin/env python3

import argparse
import json
import sys
from typing import Optional

from .extension import Extension, Browser, InvalidExtensionIDError
from .risk import get_risk_report


def get_version() -> None:
    """Print the tool version."""
    print("Chrome/Edge Extension Analyzer v1.0.0")


def analyze(id, browser, output, max_files=None, max_urls=None, permissions=False) -> None:
    """
    Analyze a browser extension and generate a risk assessment report.
    
    Args:
        id: Extension ID to analyze
        browser: Browser type ('chrome' or 'edge')
        output: Output format ('pretty' or 'json')
        max_files: Maximum number of JavaScript files to display
        max_urls: Maximum number of URLs to display
        permissions: Show only permissions and metadata
    """
    try:
        browser_enum = Browser.CHROME if browser.lower() == 'chrome' else Browser.EDGE
        
        with Extension(id, browser_enum) as ext:
            risk_report = get_risk_report(ext)
            
            if output.lower() == 'json':
                print(json.dumps(risk_report, indent=2, default=str))
            else:
                _print_pretty_report(risk_report, max_files, max_urls, permissions)
                
    except InvalidExtensionIDError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


def _print_pretty_report(report, max_files, max_urls, permissions_only) -> None:
    """Print a formatted risk assessment report to the console."""
    
    # Print metadata
    print(f"\n{'='*60}")
    print(f"EXTENSION ANALYSIS REPORT")
    print(f"{'='*60}")
    print(f"Name: {report.get('name', 'N/A')}")
    print(f"Version: {report.get('version', 'N/A')}")
    print(f"Author: {report.get('author', 'N/A')}")
    print(f"Browser: {report.get('browser', 'N/A')}")
    print(f"Extension ID: {report.get('extension_id', 'N/A')}")
    print(f"Manifest Version: {report.get('manifest_version', 'N/A')}")
    print(f"SHA256: {report.get('sha256', 'N/A')}")
    print(f"Homepage URL: {report.get('homepage_url', 'N/A')}")
    
    # Print risk score
    risk_score = report.get('risk_score', 0)
    print(f"\nOverall Risk Score: {risk_score}/100")
    
    # Print permissions with risk levels
    print(f"\n{'='*60}")
    print(f"PERMISSIONS")
    print(f"{'='*60}")
    
    permissions = report.get('permissions', [])
    for perm in permissions:
        permission = perm.get('permission', 'N/A')
        risk_level = perm.get('risk_level', 'N/A')
        risk_score_val = perm.get('risk_score', 0)
        
        # Color coding based on risk level
        color_code = ""
        if risk_level == "CRITICAL":
            color_code = "\033[91m"  # Red
        elif risk_level == "HIGH":
            color_code = "\033[93m"  # Yellow
        elif risk_level == "MEDIUM":
            color_code = "\033[33m"  # Orange
        elif risk_level == "LOW":
            color_code = "\033[92m"  # Green
        elif risk_level == "NONE":
            color_code = "\033[94m"  # Blue
        
        print(f"{color_code}{permission} ({risk_level}, Score: {risk_score_val})\033[0m")
    
    if permissions_only:
        return
    
    # Print JavaScript files
    js_files = report.get('javascript_files', [])
    print(f"\n{'='*60}")
    print(f"JAVASCRIPT FILES ({len(js_files)})")
    print(f"{'='*60}")
    
    files_to_show = js_files[:max_files] if max_files else js_files
    for i, file in enumerate(files_to_show, 1):
        print(f"{i}. {file}")
    
    if max_files and len(js_files) > max_files:
        print(f"... and {len(js_files) - max_files} more files")
    
    # Print URLs
    urls = report.get('urls', [])
    print(f"\n{'='*60}")
    print(f"REFERENCED URLS ({len(urls)})")
    print(f"{'='*60}")
    
    urls_to_show = urls[:max_urls] if max_urls else urls
    for i, url in enumerate(urls_to_show, 1):
        print(f"{i}. {url}")
    
    if max_urls and len(urls) > max_urls:
        print(f"... and {len(urls) - max_urls} more URLs")


def cli() -> None:
    """Command line interface for the extension analyzer."""
    parser = argparse.ArgumentParser(
        description="Chrome/Edge Extension Analyzer - Security risk assessment tool"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Version command
    version_parser = subparsers.add_parser('version', help='Show tool version')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze an extension')
    analyze_parser.add_argument('id', help='Extension ID to analyze')
    analyze_parser.add_argument('--browser', choices=['chrome', 'edge'], 
                               default='chrome', help='Browser type (default: chrome)')
    analyze_parser.add_argument('--output', choices=['pretty', 'json'], 
                               default='pretty', help='Output format (default: pretty)')
    analyze_parser.add_argument('--max-files', type=int, 
                               help='Maximum number of JavaScript files to display')
    analyze_parser.add_argument('--max-urls', type=int, 
                               help='Maximum number of URLs to display')
    analyze_parser.add_argument('--permissions', action='store_true',
                               help='Show only permissions and metadata')
    
    args = parser.parse_args()
    
    if args.command == 'version':
        get_version()
    elif args.command == 'analyze':
        analyze(
            id=args.id,
            browser=args.browser,
            output=args.output,
            max_files=args.max_files,
            max_urls=args.max_urls,
            permissions=args.permissions
        )
    else:
        parser.print_help()


if __name__ == '__main__':
    cli()