import requests
from bs4 import BeautifulSoup

r = requests.get('https://help.gohighlevel.com/support/solutions')
soup = BeautifulSoup(r.content, 'html.parser')

print(f"Status code: {r.status_code}")
print(f"Content length: {len(r.content)}")

sections = soup.find_all('section', class_='fw-category-wrapper')
print(f'\nfw-category-wrapper sections: {len(sections)}')

h3_titles = soup.find_all('h3', class_='fw-category-title')
print(f'fw-category-title h3s: {len(h3_titles)}')

if h3_titles:
    print(f'First title: {h3_titles[0].get_text(strip=True)}')

h3_all = soup.find_all('h3')
print(f'\nTotal h3 tags: {len(h3_all)}')

for i, h in enumerate(h3_all[:5]):
    print(f'  h3 {i}: classes={h.get("class", [])}, text={h.get_text(strip=True)[:50]}')

# Look for any links that might be category links
category_links = soup.find_all('a', href=lambda x: x and '/support/solutions/' in x and 'articles' not in x)
print(f'\nCategory-like links: {len(category_links)}')
for i, link in enumerate(category_links[:5]):
    print(f'  {i}: {link.get_text(strip=True)[:50]} -> {link["href"]}')
