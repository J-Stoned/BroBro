#!/usr/bin/env python3
"""
BroBro - Official Documentation Scraper
Scrapes help.gohighlevel.com for comprehensive documentation
"""

import os
import json
import time
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

class GHLDocScraper:
    """Scrapes GoHighLevel official documentation"""

    def __init__(self, output_dir: str):
        self.base_url = "https://help.gohighlevel.com"
        self.output_dir = Path(output_dir)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'GHL-WIZ-Documentation-Scraper/1.0 (Educational Purpose)'
        })

        # Statistics
        self.stats = {
            'categories_found': 0,
            'articles_found': 0,
            'articles_scraped': 0,
            'articles_failed': 0,
            'total_words': 0,
            'errors': []
        }

        # Create output directories
        self.create_directories()

    def create_directories(self):
        """Create output directory structure"""
        directories = [
            self.output_dir,
            self.output_dir / 'by-category',
            self.output_dir / 'all-articles'
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

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
                    self.stats['errors'].append({
                        'url': url,
                        'error': str(e)
                    })
                    print(f"  Failed to fetch: {e}")
                    return None
                time.sleep(2 ** attempt)  # Exponential backoff
        return None

    def get_all_categories(self) -> List[Dict]:
        """Get all solution categories from the main solutions page"""
        print("\n" + "="*80)
        print("Fetching Solution Categories...")
        print("="*80)

        url = f"{self.base_url}/support/solutions"
        soup = self.fetch_page(url)

        if not soup:
            print("Failed to fetch categories page")
            return []

        categories = []

        # Find all category sections (using fw-category-wrapper class from Freshdesk)
        category_sections = soup.find_all('section', class_='fw-category-wrapper')

        for section in category_sections:
            # Get category title and URL from h2 tag
            category_header = section.find('h2')
            if not category_header:
                continue

            category_link = category_header.find('a')

            if category_link:
                category_title = category_link.get_text(strip=True)
                category_url = urljoin(self.base_url, category_link['href'])
                category_id = category_url.split('/')[-1]

                # Count folders (h3 elements) in this category
                folder_elements = section.find_all('h3', class_='semi-bold')
                folder_count = len(folder_elements)

                categories.append({
                    'id': category_id,
                    'title': category_title,
                    'url': category_url,
                    'folder_count': folder_count
                })

                print(f"  Found: {category_title} ({folder_count} folders)")

        self.stats['categories_found'] = len(categories)
        print(f"\nTotal Categories: {len(categories)}")

        return categories

    def get_category_articles(self, category: Dict) -> List[Dict]:
        """Get all articles from a specific category"""
        print(f"\n{'-'*80}")
        print(f"Category: {category['title']}")
        print(f"{'-'*80}")

        soup = self.fetch_page(category['url'])

        if not soup:
            return []

        articles = []

        # Find all folders in the category
        folders = soup.find_all('div', class_='fw-folder-wrapper')

        for folder in folders:
            # Get folder name
            folder_header = folder.find('h4', class_='fw-folder-title')
            folder_name = folder_header.get_text(strip=True) if folder_header else "General"

            # Find all article links in this folder
            article_items = folder.find_all('li', class_='fw-article-list-item')

            for item in article_items:
                link = item.find('a')

                if link:
                    article_title = link.get_text(strip=True)
                    article_url = urljoin(self.base_url, link['href'])
                    # Extract article ID from URL like /support/solutions/articles/155000005055-title
                    article_id = article_url.split('/articles/')[-1].split('-')[0]

                    articles.append({
                        'id': article_id,
                        'title': article_title,
                        'url': article_url,
                        'category': category['title'],
                        'category_id': category['id'],
                        'folder': folder_name
                    })

        print(f"  Found {len(articles)} articles")

        return articles

    def scrape_article(self, article: Dict) -> Optional[Dict]:
        """Scrape content from a single article"""
        soup = self.fetch_page(article['url'])

        if not soup:
            self.stats['articles_failed'] += 1
            return None

        # Extract article content
        article_body = soup.find('div', class_='article-body')

        if not article_body:
            article_body = soup.find('article')

        if not article_body:
            print(f"  No content found for: {article['title']}")
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
            'category_id': article['category_id'],
            'word_count': word_count,
            'scraped_date': datetime.now().isoformat(),
            'content_length': len(content)
        }

        # Try to get last updated date
        date_element = soup.find('time')
        if date_element:
            metadata['last_updated'] = date_element.get('datetime', '')

        self.stats['articles_scraped'] += 1

        return {
            'metadata': metadata,
            'content': content
        }

    def save_article(self, article_data: Dict, category_name: str):
        """Save article to file"""
        metadata = article_data['metadata']
        content = article_data['content']

        # Sanitize filename
        safe_title = re.sub(r'[^\w\s-]', '', metadata['title'])
        safe_title = re.sub(r'[-\s]+', '-', safe_title)
        safe_title = safe_title[:100]  # Limit length

        filename = f"{metadata['id']}_{safe_title}.txt"

        # Save to category directory
        category_safe = re.sub(r'[^\w\s-]', '', category_name)
        category_safe = re.sub(r'[-\s]+', '-', category_safe)
        category_dir = self.output_dir / 'by-category' / category_safe
        category_dir.mkdir(parents=True, exist_ok=True)

        category_path = category_dir / filename

        # Save to all-articles directory
        all_path = self.output_dir / 'all-articles' / filename

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

        # Write to both locations
        with open(category_path, 'w', encoding='utf-8') as f:
            f.write(file_content)

        with open(all_path, 'w', encoding='utf-8') as f:
            f.write(file_content)

    def save_index(self, all_articles: List[Dict]):
        """Save index of all scraped articles"""
        index = {
            'generated_date': datetime.now().isoformat(),
            'total_articles': len(all_articles),
            'total_categories': self.stats['categories_found'],
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

        # Get all categories
        categories = self.get_all_categories()

        if not categories:
            print("\nNo categories found. Exiting.")
            return

        all_articles_data = []
        articles_processed = 0

        # Process each category
        for i, category in enumerate(categories, 1):
            print(f"\n[{i}/{len(categories)}] Processing: {category['title']}")

            # Get articles in this category
            articles = self.get_category_articles(category)
            self.stats['articles_found'] += len(articles)

            # Scrape each article
            for j, article in enumerate(articles, 1):
                if max_articles and articles_processed >= max_articles:
                    print(f"\nReached max articles limit ({max_articles})")
                    break

                print(f"  [{j}/{len(articles)}] {article['title'][:60]}...", end='')

                # Scrape article
                article_data = self.scrape_article(article)

                if article_data:
                    # Save article
                    self.save_article(article_data, category['title'])
                    all_articles_data.append(article_data['metadata'])
                    print(f" OK ({article_data['metadata']['word_count']} words)")
                else:
                    print(" FAILED")

                articles_processed += 1

                # Rate limiting: 1 second between requests
                time.sleep(1)

            if max_articles and articles_processed >= max_articles:
                break

            # Longer delay between categories
            time.sleep(2)

        # Save index
        self.save_index(all_articles_data)

        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print scraping summary"""
        print("\n" + "="*80)
        print("SCRAPING COMPLETE")
        print("="*80)
        print(f"Categories Found: {self.stats['categories_found']}")
        print(f"Articles Found: {self.stats['articles_found']}")
        print(f"Articles Scraped: {self.stats['articles_scraped']}")
        print(f"Articles Failed: {self.stats['articles_failed']}")
        print(f"Total Words: {self.stats['total_words']:,}")
        print(f"Average Words/Article: {self.stats['total_words'] // max(self.stats['articles_scraped'], 1):,}")

        if self.stats['errors']:
            print(f"\nErrors: {len(self.stats['errors'])}")
            for error in self.stats['errors'][:5]:  # Show first 5 errors
                print(f"  - {error['url']}: {error['error']}")

        print(f"\nOutput Directory: {self.output_dir}")
        print(f"  - by-category/: Articles organized by category")
        print(f"  - all-articles/: All articles in one directory")
        print(f"  - index.json: Complete index with metadata")

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

    scraper = GHLDocScraper(args.output)
    scraper.scrape_all(max_articles=args.max_articles)

if __name__ == '__main__':
    main()
