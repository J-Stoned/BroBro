import requests
from bs4 import BeautifulSoup

r = requests.get('https://help.gohighlevel.com/support/solutions')
soup = BeautifulSoup(r.content, 'html.parser')

# Find all article links on main page
article_links = soup.find_all('a', href=lambda x: x and '/support/solutions/articles/' in x)
print(f"Total article links on main page: {len(article_links)}")

if article_links:
    print("\nFirst 5 articles:")
    for i, link in enumerate(article_links[:5]):
        print(f"  {i+1}. {link.get_text(strip=True)}")
        print(f"     {link['href']}")
