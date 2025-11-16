#!/usr/bin/env python3
"""
BroBro - Retry Failed Documentation Scrapes
Retries the 16 URLs that previously failed with HTTP 408/429 errors
"""

import os
import json
import time
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup

class FailedScrapeRetry:
    """Retry failed documentation scrapes"""

    def __init__(self, output_dir: str = "kb/ghl-docs"):
        self.output_dir = Path(output_dir)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

        # Load failed URLs from previous report
        self.failed_urls = [
            "https://help.gohighlevel.com/support/solutions/articles/155000001156-highlevel-pricing-guide",
            "https://help.gohighlevel.com/support/solutions/articles/48000982207-how-to-set-up-a-whitelabel-domain-for-the-desktop-web-app",
            "https://help.gohighlevel.com/support/solutions/articles/48001153720-how-to-set-up-root-domain-subdomain-for-your-funnels-websites-",
            "https://help.gohighlevel.com/support/solutions/articles/48001223556-lc-phone-pricing-billing-guide",
            "https://help.gohighlevel.com/support/solutions/articles/48001184920-saas-mode-full-setup-guide-faq",
            "https://help.gohighlevel.com/support/solutions/articles/48001226115-dedicated-email-sending-domains-overview-setup",
            "https://marketplace.gohighlevel.com/docs/Authorization/authorization_doc",
            "https://marketplace.gohighlevel.com/docs/category/webhook",
            "https://marketplace.gohighlevel.com/docs/ghl/calendars/calendars",
            "https://marketplace.gohighlevel.com/docs/ghl/contacts/contacts",
            "https://marketplace.gohighlevel.com/docs/ghl/conversations/conversations",
            "https://marketplace.gohighlevel.com/docs/ghl/opportunities/opportunities",
            "https://marketplace.gohighlevel.com/docs/ghl/payments/integrations",
            "https://help.gohighlevel.com/support/solutions/articles/48001204848-how-do-i-find-my-client-s-location-id-",
            "https://help.gohighlevel.com/support/solutions/articles/48001213941-lc-phone-messaging-policy",
            "https://help.gohighlevel.com/support/solutions/articles/48001223546-what-is-lc-lead-connector-phone-system-"
        ]

        self.stats = {
            'total_urls': len(self.failed_urls),
            'successful': 0,
            'failed': 0,
            'results': []
        }

    def sanitize_filename(self, text: str) -> str:
        """Create safe filename from text"""
        safe = re.sub(r'[^\w\s-]', '', text)
        safe = re.sub(r'[-\s]+', '-', safe)
        return safe[:100]

    def extract_article_id(self, url: str) -> Optional[str]:
        """Extract article ID from URL"""
        match = re.search(r'/articles/(\d+)', url)
        if match:
            return match.group(1)
        # For marketplace docs
        match = re.search(r'/docs/([^/]+)', url)
        if match:
            return match.group(1).replace('/', '_')
        return None

    def scrape_help_article(self, url: str) -> Optional[Dict]:
        """Scrape a help.gohighlevel.com article"""
        try:
            print(f"\n  Fetching: {url}")
            response = self.session.get(url, timeout=45)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract title
            title_elem = soup.find('h1') or soup.find('title')
            title = title_elem.get_text(strip=True) if title_elem else "Untitled"

            # Extract category
            category_elem = soup.find('a', {'class': 'breadcrumb-link'})
            category = category_elem.get_text(strip=True) if category_elem else "Uncategorized"

            # Extract main content
            content_elem = soup.find('div', {'class': 'article-body'}) or soup.find('article')
            if not content_elem:
                return None

            content = content_elem.get_text(separator='\n', strip=True)
            word_count = len(content.split())

            return {
                'title': title,
                'category': category,
                'content': content,
                'url': url,
                'word_count': word_count,
                'scraped_at': datetime.now().isoformat()
            }

        except Exception as e:
            print(f"    Error: {e}")
            return None

    def scrape_marketplace_doc(self, url: str) -> Optional[Dict]:
        """Scrape a marketplace.gohighlevel.com doc"""
        try:
            print(f"\n  Fetching: {url}")
            response = self.session.get(url, timeout=45)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract title
            title_elem = soup.find('h1')
            title = title_elem.get_text(strip=True) if title_elem else "Untitled"

            # Extract main content
            content_elem = soup.find('main') or soup.find('article')
            if not content_elem:
                return None

            content = content_elem.get_text(separator='\n', strip=True)
            word_count = len(content.split())

            return {
                'title': title,
                'category': 'API Documentation',
                'content': content,
                'url': url,
                'word_count': word_count,
                'scraped_at': datetime.now().isoformat()
            }

        except Exception as e:
            print(f"    Error: {e}")
            return None

    def save_article(self, article_data: Dict, article_id: str):
        """Save article to file"""
        title = article_data['title']
        safe_title = self.sanitize_filename(title)
        filename = f"{article_id}_{safe_title}.txt"
        filepath = self.output_dir / filename

        # Create content with metadata header
        content = f"""---
Title: {title}
Category: {article_data['category']}
URL: {article_data['url']}
Word Count: {article_data['word_count']}
Scraped: {article_data['scraped_at']}
---

{article_data['content']}
"""

        filepath.write_text(content, encoding='utf-8')
        print(f"    Saved: {filename}")

    def retry_all(self):
        """Retry all failed URLs with delays"""
        print("="*80)
        print("BroBro - Retry Failed Documentation Scrapes")
        print("="*80)
        print(f"\nRetrying {len(self.failed_urls)} failed URLs...")
        print(f"Output: {self.output_dir}")

        for i, url in enumerate(self.failed_urls, 1):
            print(f"\n[{i}/{len(self.failed_urls)}] Retrying: {url}")

            # Determine scraper method
            if 'marketplace.gohighlevel.com' in url:
                article_data = self.scrape_marketplace_doc(url)
            else:
                article_data = self.scrape_help_article(url)

            if article_data:
                # Extract article ID
                article_id = self.extract_article_id(url)
                if not article_id:
                    article_id = f"retry_{i}"

                # Save article
                self.save_article(article_data, article_id)

                self.stats['successful'] += 1
                self.stats['results'].append({
                    'url': url,
                    'status': 'success',
                    'word_count': article_data['word_count']
                })
                print(f"    SUCCESS ({article_data['word_count']} words)")
            else:
                self.stats['failed'] += 1
                self.stats['results'].append({
                    'url': url,
                    'status': 'failed',
                    'error': 'Could not extract content'
                })
                print(f"    FAILED")

            # Rate limiting: wait between requests
            if i < len(self.failed_urls):
                wait_time = 5  # 5 seconds between requests
                print(f"    Waiting {wait_time}s...")
                time.sleep(wait_time)

        # Save report
        self.save_report()

    def save_report(self):
        """Save retry report"""
        report_path = self.output_dir / 'retry-report.json'
        self.stats['timestamp'] = datetime.now().isoformat()

        with open(report_path, 'w') as f:
            json.dump(self.stats, f, indent=2)

        print("\n" + "="*80)
        print("RETRY SUMMARY")
        print("="*80)
        print(f"Total URLs: {self.stats['total_urls']}")
        print(f"Successful: {self.stats['successful']}")
        print(f"Failed: {self.stats['failed']}")
        print(f"Success Rate: {self.stats['successful'] / self.stats['total_urls'] * 100:.1f}%")
        print(f"\nReport saved: {report_path}")

if __name__ == "__main__":
    scraper = FailedScrapeRetry()
    scraper.retry_all()
