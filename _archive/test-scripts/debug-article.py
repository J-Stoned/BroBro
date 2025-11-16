import requests
from bs4 import BeautifulSoup

# Fetch a specific article
url = 'https://help.gohighlevel.com/support/solutions/articles/155000005055-getting-started-create-new-contact'
r = requests.get(url)
soup = BeautifulSoup(r.content, 'html.parser')

print("Article Page Structure")
print("="*80)
print(f"Status: {r.status_code}")
print(f"Content length: {len(r.content)}")

# Try different selectors
selectors = [
    ('div.article-body', soup.find('div', class_='article-body')),
    ('article', soup.find('article')),
    ('div.article-content', soup.find('div', class_='article-content')),
    ('div#article-desc', soup.find('div', id='article-desc')),
    ('div.fw-article-body', soup.find('div', class_='fw-article-body')),
    ('main', soup.find('main')),
]

for selector, element in selectors:
    if element:
        text = element.get_text(strip=True)[:200]
        print(f"\n{selector}: FOUND")
        print(f"  Text preview: {text}...")
    else:
        print(f"\n{selector}: NOT FOUND")

# Look for any divs with 'article' or 'content' in class name
print("\n\nDivs with 'article' or 'content' in class:")
all_divs = soup.find_all('div', class_=True)
for div in all_divs:
    classes = ' '.join(div.get('class', []))
    if 'article' in classes.lower() or 'content' in classes.lower():
        print(f"  {classes}")
        if len(classes) < 50:  # Only short class names
            text = div.get_text(strip=True)[:100]
            if len(text) > 50:  # Has substantial text
                print(f"    -> {text}...")
