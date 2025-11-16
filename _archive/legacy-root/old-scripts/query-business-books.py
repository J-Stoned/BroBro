#!/usr/bin/env python3
"""
Query ALL Business Books for Marketing Agency Advice
Specialized script for extracting actionable business wisdom
"""

import sys
import json
from pathlib import Path

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def load_all_books(books_dir="./data/books"):
    """Load all business books from JSON files"""
    books_path = Path(books_dir)
    all_books = []
    
    print(f"\n{'='*80}")
    print("📚 LOADING YOUR 21-BOOK BUSINESS LIBRARY")
    print(f"{'='*80}\n")
    
    for book_file in books_path.glob("*.json"):
        try:
            with open(book_file, 'r', encoding='utf-8') as f:
                book_data = json.load(f)
                
                title = book_data.get('title', book_file.stem)
                author = book_data.get('author', 'Unknown')
                entries = book_data.get('entries', [])
                
                # Combine all text
                full_text = " ".join([entry.get('text', '') for entry in entries])
                word_count = len(full_text.split())
                
                all_books.append({
                    'title': title,
                    'author': author,
                    'text': full_text,
                    'word_count': word_count
                })
                
                print(f"✓ {title}")
                print(f"  By: {author} | Words: {word_count:,}")
                
        except Exception as e:
            print(f"✗ Error loading {book_file.name}: {e}")
    
    total_words = sum(b['word_count'] for b in all_books)
    print(f"\n{'='*80}")
    print(f"📊 TOTAL: {len(all_books)} books | {total_words:,} words")
    print(f"{'='*80}\n")
    
    return all_books

def extract_marketing_insights(books, topic="marketing agency growth"):
    """Extract relevant insights based on topic"""
    
    # Keywords for marketing agency growth
    keywords = {
        'client_acquisition': ['get clients', 'acquire customers', 'client acquisition', 
                              'customer acquisition', 'find clients', 'attract clients'],
        'pricing': ['pricing strategy', 'charge more', 'premium pricing', 'price point',
                   'value pricing', 'pricing power'],
        'positioning': ['niche', 'target market', 'positioning', 'differentiation',
                       'unique selling', 'value proposition'],
        'sales': ['sales strategy', 'selling', 'close deals', 'conversion',
                 'sales process', 'pitch'],
        'growth': ['scale business', 'grow revenue', 'business growth', 'scaling',
                  'expansion', 'growth strategy'],
        'offers': ['offer creation', 'irresistible offer', 'grand slam offer',
                  'value stack', 'guarantee'],
        'marketing': ['marketing strategy', 'lead generation', 'advertising',
                     'marketing funnel', 'traffic']
    }
    
    print(f"\n{'='*80}")
    print(f"🔍 EXTRACTING INSIGHTS: {topic.upper()}")
    print(f"{'='*80}\n")
    
    insights_by_category = {}
    
    for category, terms in keywords.items():
        insights_by_category[category] = []
        
        for book in books:
            text_lower = book['text'].lower()
            
            for term in terms:
                if term in text_lower:
                    # Find all occurrences
                    start = 0
                    while True:
                        idx = text_lower.find(term, start)
                        if idx == -1:
                            break
                        
                        # Extract context (300 chars before/after)
                        context_start = max(0, idx - 300)
                        context_end = min(len(book['text']), idx + 300)
                        passage = book['text'][context_start:context_end]
                        
                        # Clean passage
                        passage = passage.replace('\n', ' ').replace('  ', ' ').strip()
                        
                        insights_by_category[category].append({
                            'book': book['title'],
                            'keyword': term,
                            'passage': passage
                        })
                        
                        start = idx + len(term)
                        
                        # Limit to 5 passages per book per term
                        if start > idx + 5000:
                            break
    
    return insights_by_category

def synthesize_advice(insights_by_category):
    """Synthesize key advice from all insights"""
    
    print(f"\n{'='*80}")
    print("💡 SYNTHESIZED MARKETING AGENCY GROWTH ADVICE")
    print(f"{'='*80}\n")
    
    for category, insights in insights_by_category.items():
        if not insights:
            continue
        
        print(f"\n### {category.upper().replace('_', ' ')} ({len(insights)} insights)")
        print("-" * 80)
        
        # Get unique books with insights
        books_with_insights = list(set(i['book'] for i in insights[:10]))
        
        # Show top 3 most relevant passages
        for insight in insights[:3]:
            print(f"\n📖 {insight['book']}")
            print(f"   Keyword: '{insight['keyword']}'")
            print(f"\n   {insight['passage'][:400]}...")
            print()

def main():
    """Main execution"""
    
    # Load all books
    books = load_all_books()
    
    if not books:
        print("❌ No books found! Check your data/books directory.")
        return 1
    
    # Extract insights
    insights = extract_marketing_insights(books)
    
    # Synthesize and display
    synthesize_advice(insights)
    
    # Summary stats
    print(f"\n{'='*80}")
    print("📊 SUMMARY")
    print(f"{'='*80}\n")
    
    total_insights = sum(len(v) for v in insights.values())
    print(f"Total insights extracted: {total_insights}")
    
    for category, category_insights in insights.items():
        if category_insights:
            unique_books = len(set(i['book'] for i in category_insights))
            print(f"  • {category.replace('_', ' ').title()}: {len(category_insights)} insights from {unique_books} books")
    
    print(f"\n{'='*80}\n")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
