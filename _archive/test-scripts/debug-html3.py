import requests
from bs4 import BeautifulSoup

# Fetch a specific category page
r = requests.get('https://help.gohighlevel.com/support/solutions/155000000204')
soup = BeautifulSoup(r.content, 'html.parser')

print("Category Page Structure")
print("="*80)

# Look for article lists
article_items = soup.find_all('li', class_='fw-article-list-item')
print(f"\nfw-article-list-item: {len(article_items)}")

if article_items:
    first = article_items[0]
    link = first.find('a')
    if link:
        print(f"First article: {link.get_text(strip=True)}")
        print(f"  href: {link['href']}")

# Look for folders
folder_wrappers = soup.find_all('div', class_='fw-folder-wrapper')
print(f"\nfw-folder-wrapper divs: {len(folder_wrappers)}")

if folder_wrappers:
    first_folder = folder_wrappers[0]
    h3 = first_folder.find('h3')
    h4 = first_folder.find('h4')
    print(f"First folder h3: {h3.get_text(strip=True) if h3 else 'None'}")
    print(f"First folder h4: {h4.get_text(strip=True) if h4 else 'None'}")

    articles_in_folder = first_folder.find_all('li', class_='fw-article-list-item')
    print(f"Articles in first folder: {len(articles_in_folder)}")
