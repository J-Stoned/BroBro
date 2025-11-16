"""
BroBro - Best Practices Content Scraper
Scrapes best practices, guides, and implementation tips from multiple sources
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import re

class BestPracticesScraper:
    """Scrapes GHL best practices from multiple sources"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.output_dir = Path('data/best-practices')
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def scrape_blog_article(self, url: str) -> Optional[Dict]:
        """Scrape a single blog article"""
        try:
            print(f"  >> Fetching: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract title
            title = None
            title_selectors = ['h1', 'h1.title', 'h1.post-title', '.article-title']
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    break

            if not title:
                print(f"  [WARN] Could not find title for {url}")
                return None

            # Extract main content
            content = None
            content_selectors = [
                'article',
                '.post-content',
                '.article-content',
                '.entry-content',
                'main',
                '.content'
            ]

            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    # Remove script and style elements
                    for script in content_elem(['script', 'style', 'nav', 'footer', 'aside']):
                        script.decompose()

                    content = content_elem.get_text(separator='\n', strip=True)
                    break

            if not content or len(content) < 100:
                print(f"  [WARN] Content too short or not found for {url}")
                return None

            # Extract metadata
            meta_description = soup.find('meta', {'name': 'description'})
            description = meta_description.get('content', '') if meta_description else ''

            # Extract categories/tags
            categories = []
            for tag_elem in soup.select('.category, .tag, [class*="category"], [class*="tag"]'):
                cat_text = tag_elem.get_text(strip=True)
                if cat_text and len(cat_text) < 50:
                    categories.append(cat_text)

            word_count = len(content.split())

            article_data = {
                'title': title,
                'url': url,
                'content': content,
                'description': description,
                'categories': categories[:5],  # Limit to 5 categories
                'word_count': word_count,
                'scraped_date': datetime.now().isoformat(),
                'source_type': 'blog_article'
            }

            print(f"  [OK] Scraped: {title} ({word_count} words)")
            return article_data

        except Exception as e:
            print(f"  [ERROR] Failed to scrape {url}: {e}")
            return None

    def scrape_help_article(self, article_url: str) -> Optional[Dict]:
        """Scrape a help center article"""
        try:
            print(f"  >> Fetching help article: {article_url}")
            response = self.session.get(article_url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract title
            title_elem = soup.select_one('h1, .article-title, .page-title')
            if not title_elem:
                return None
            title = title_elem.get_text(strip=True)

            # Extract article content
            content_elem = soup.select_one('article, .article-body, .article-content, .content')
            if not content_elem:
                return None

            # Clean up
            for elem in content_elem(['script', 'style', 'nav', 'footer']):
                elem.decompose()

            content = content_elem.get_text(separator='\n', strip=True)

            # Extract category from breadcrumbs or page structure
            category = None
            breadcrumb = soup.select_one('.breadcrumb, .breadcrumbs')
            if breadcrumb:
                crumbs = breadcrumb.get_text(strip=True)
                category = crumbs

            word_count = len(content.split())

            if word_count < 50:
                print(f"  [SKIP] Article too short: {title}")
                return None

            article_data = {
                'title': title,
                'url': article_url,
                'content': content,
                'category': category or 'General',
                'word_count': word_count,
                'scraped_date': datetime.now().isoformat(),
                'source_type': 'help_article'
            }

            print(f"  [OK] Scraped help: {title} ({word_count} words)")
            return article_data

        except Exception as e:
            print(f"  [ERROR] Failed to scrape help article: {e}")
            return None

    def save_articles(self, articles: List[Dict], filename: str):
        """Save scraped articles to JSON file"""
        output_path = self.output_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=2, ensure_ascii=False)
        print(f"\n[OK] Saved {len(articles)} articles to {output_path}")

    def scrape_curated_sources(self) -> List[Dict]:
        """Scrape curated best practices sources"""

        print("\n" + "="*70)
        print("BroBro - Best Practices Scraper")
        print("="*70)

        articles = []

        # Curated list of best practice articles
        sources = [
            # Best practices guides
            'https://viasocket.com/blog/10-best-practices-for-using-gohighlevel-in-2025/',
            'https://gohighlevele.com/highlevel-help/building-a-thriving-gohighlevel-community/',
            'https://howtohighlevel.com/building-a-thriving-gohighlevel-community',

            # Official help articles on best practices
            'https://help.gohighlevel.com/support/solutions/articles/155000000280-how-to-setup-customize-and-manage-your-communities',
            'https://help.gohighlevel.com/support/solutions/articles/155000005055-getting-started-create-new-contact',
            'https://help.gohighlevel.com/support/solutions/articles/155000005057-getting-started-launch-a-funnel',

            # Add more URLs as needed
        ]

        print(f"\n>> Scraping {len(sources)} curated sources...\n")

        for url in sources:
            article = self.scrape_blog_article(url)
            if article:
                articles.append(article)
            time.sleep(2)  # Be respectful with rate limiting

        return articles

    def scrape_ghl_blog_listing(self) -> List[Dict]:
        """Scrape multiple articles from GHL blog"""

        print("\n>> Scraping GHL official blog...")

        blog_urls = [
            'https://www.gohighlevel.com/blog/did-you-know-you-can-run-a-referral-program-in-highlevel',
            'https://www.gohighlevel.com/blog/did-you-know-highlevel-can-email-leads-the-second-they-hit-submit',
            'https://www.gohighlevel.com/blog/did-you-know-you-can-create-branded-dashboards-with-highlevel',
            'https://www.gohighlevel.com/blog/did-you-know-highlevel-can-turn-missed-calls-into-booked-appointments-for-you',
        ]

        articles = []
        for url in blog_urls:
            article = self.scrape_blog_article(url)
            if article:
                articles.append(article)
            time.sleep(2)

        return articles


def main():
    scraper = BestPracticesScraper()

    # Scrape all sources
    all_articles = []

    # Scrape curated best practices
    curated = scraper.scrape_curated_sources()
    all_articles.extend(curated)

    # Scrape GHL blog
    blog_articles = scraper.scrape_ghl_blog_listing()
    all_articles.extend(blog_articles)

    # Save results
    if all_articles:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        scraper.save_articles(all_articles, f'best-practices_{timestamp}.json')

        print("\n" + "="*70)
        print(f"[SUCCESS] Scraped {len(all_articles)} best practice articles")
        print("="*70)

        # Summary
        total_words = sum(a['word_count'] for a in all_articles)
        print(f"\nTotal words: {total_words:,}")
        print(f"Average words per article: {total_words // len(all_articles):,}")
    else:
        print("\n[WARN] No articles were scraped successfully")


if __name__ == "__main__":
    main()
