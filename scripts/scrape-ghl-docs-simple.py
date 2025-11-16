#!/usr/bin/env python3
"""
BroBro - Official Documentation Scraper (Simplified)
Scrapes help.gohighlevel.com directly from the main solutions page
"""

import os
import json
import time
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

class GHLDocScraperSimple:
    """Simplified GHL Documentation Scraper"""

    def __init__(self, output_dir: str):
        self.base_url = "https://help.gohighlevel.com"
        self.output_dir = Path(output_dir)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'GHL-WIZ-Documentation-Scraper/1.0 (Educational Purpose)'
        })

        # Statistics
        self.stats = {
            'articles_found': 0,
            'articles_scraped': 0,
            'articles_failed': 0,
            'total_words': 0,
            'errors': []
        }

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        print(f"Output directory: {self.output_dir}")

    def fetch_page(self, url: str, retries: int = 3) -> Optional[BeautifulSoup]:
        """Fetch and parse a page with retry logic"""
        for attempt in range(retries):
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                return BeautifulSoup(response.content, 'html.parser')
            except Exception as e:
                if attempt == retries - 1:
                    self.stats['errors'].append({'url': url, 'error': str(e)})
                    print(f"  Failed to fetch: {e}")
                    return None
                time.sleep(2 ** attempt)
        return None

    def get_all_article_links(self) -> List[Dict]:
        """Get all article links from the main solutions page"""
        print("\n" + "="*80)
        print("Fetching Article Links from Main Page...")
        print("="*80)

        url = f"{self.base_url}/support/solutions"
        soup = self.fetch_page(url)

        if not soup:
            print("Failed to fetch main solutions page")
            return []

        articles = []

        # Find all article links
        article_links = soup.find_all('a', href=lambda x: x and '/support/solutions/articles/' in x)

        print(f"Found {len(article_links)} article links")

        for link in article_links:
            article_title = link.get_text(strip=True)
            article_url = urljoin(self.base_url, link['href'])
            article_id = article_url.split('/articles/')[-1].split('-')[0]

            # Try to determine category from surrounding context
            category = self.get_category_from_context(link)

            articles.append({
                'id': article_id,
                'title': article_title,
                'url': article_url,
                'category': category
            })

        # Remove duplicates based on article ID
        seen_ids = set()
        unique_articles = []
        for article in articles:
            if article['id'] not in seen_ids:
                seen_ids.add(article['id'])
                unique_articles.append(article)

        self.stats['articles_found'] = len(unique_articles)
        print(f"Unique articles: {len(unique_articles)}")

        return unique_articles

    def get_category_from_context(self, link_element) -> str:
        """Try to determine category from surrounding HTML context"""
        # Look for parent section with h2
        parent = link_element.find_parent('section', class_='fw-category-wrapper')
        if parent:
            h2 = parent.find('h2')
            if h2:
                return h2.get_text(strip=True)
        return "General"

    def scrape_article(self, article: Dict) -> Optional[Dict]:
        """Scrape content from a single article"""
        soup = self.fetch_page(article['url'])

        if not soup:
            self.stats['articles_failed'] += 1
            return None

        # Extract article content - try multiple selectors
        article_body = (
            soup.find('div', class_='fw-content-wrapper') or
            soup.find('div', class_='fw-content') or
            soup.find('main') or
            soup.find('div', class_='article-body') or
            soup.find('article')
        )

        if not article_body:
            print(f"  No content found")
            self.stats['articles_failed'] += 1
            return None

        # Get text content
        content = article_body.get_text(separator='\n', strip=True)

        # Remove excessive newlines
        content = re.sub(r'\n{3,}', '\n\n', content)

        # Count words
        word_count = len(content.split())
        self.stats['total_words'] += word_count

        # Extract metadata
        metadata = {
            'id': article['id'],
            'title': article['title'],
            'url': article['url'],
            'category': article['category'],
            'word_count': word_count,
            'scraped_date': datetime.now().isoformat(),
            'content_length': len(content)
        }

        self.stats['articles_scraped'] += 1

        return {
            'metadata': metadata,
            'content': content
        }

    def save_article(self, article_data: Dict):
        """Save article to file"""
        metadata = article_data['metadata']
        content = article_data['content']

        # Sanitize filename
        safe_title = re.sub(r'[^\w\s-]', '', metadata['title'])
        safe_title = re.sub(r'[-\s]+', '-', safe_title)
        safe_title = safe_title[:100]

        filename = f"{metadata['id']}_{safe_title}.txt"
        filepath = self.output_dir / filename

        # Create file content with metadata header
        file_content = f"""---
Title: {metadata['title']}
Category: {metadata['category']}
URL: {metadata['url']}
Word Count: {metadata['word_count']}
Scraped: {metadata['scraped_date']}
---

{content}
"""

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(file_content)

    def save_index(self, all_articles: List[Dict]):
        """Save index of all scraped articles"""
        index = {
            'generated_date': datetime.now().isoformat(),
            'total_articles': len(all_articles),
            'statistics': self.stats,
            'articles': all_articles
        }

        index_path = self.output_dir / 'index.json'

        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2, ensure_ascii=False)

        print(f"\nIndex saved: {index_path}")

    def scrape_all(self, max_articles: Optional[int] = None):
        """Scrape all documentation"""
        print("\n" + "="*80)
        print("BroBro - Official Documentation Scraper")
        print("="*80)
        print(f"Base URL: {self.base_url}")
        print(f"Output: {self.output_dir}")

        if max_articles:
            print(f"Max Articles: {max_articles}")

        # Get all article links
        articles = self.get_all_article_links()

        if not articles:
            print("\nNo articles found. Exiting.")
            return

        # Limit if requested
        if max_articles:
            articles = articles[:max_articles]

        all_articles_data = []

        # Scrape each article
        print("\n" + "="*80)
        print("Scraping Articles...")
        print("="*80)

        for i, article in enumerate(articles, 1):
            print(f"[{i}/{len(articles)}] {article['title'][:60]}...", end='')

            # Scrape article
            article_data = self.scrape_article(article)

            if article_data:
                # Save article
                self.save_article(article_data)
                all_articles_data.append(article_data['metadata'])
                print(f" OK ({article_data['metadata']['word_count']} words)")
            else:
                print(" FAILED")

            # Rate limiting: 1 second between requests
            time.sleep(1)

        # Save index
        self.save_index(all_articles_data)

        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print scraping summary"""
        print("\n" + "="*80)
        print("SCRAPING COMPLETE")
        print("="*80)
        print(f"Articles Found: {self.stats['articles_found']}")
        print(f"Articles Scraped: {self.stats['articles_scraped']}")
        print(f"Articles Failed: {self.stats['articles_failed']}")
        print(f"Total Words: {self.stats['total_words']:,}")

        if self.stats['articles_scraped'] > 0:
            avg = self.stats['total_words'] // self.stats['articles_scraped']
            print(f"Average Words/Article: {avg:,}")

        if self.stats['errors']:
            print(f"\nErrors: {len(self.stats['errors'])}")

        print(f"\nOutput Directory: {self.output_dir}")

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Scrape GHL official documentation')
    parser.add_argument('--output', '-o', default='kb/ghl-docs',
                       help='Output directory (default: kb/ghl-docs)')
    parser.add_argument('--max-articles', '-m', type=int, default=None,
                       help='Maximum number of articles to scrape (default: all)')
    parser.add_argument('--test', action='store_true',
                       help='Test mode: scrape only 10 articles')

    args = parser.parse_args()

    if args.test:
        args.max_articles = 10
        print("\nTEST MODE: Scraping only 10 articles\n")

    scraper = GHLDocScraperSimple(args.output)
    scraper.scrape_all(max_articles=args.max_articles)

if __name__ == '__main__':
    main()
