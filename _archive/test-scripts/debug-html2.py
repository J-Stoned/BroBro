import requests
from bs4 import BeautifulSoup

r = requests.get('https://help.gohighlevel.com/support/solutions')
soup = BeautifulSoup(r.content, 'html.parser')

sections = soup.find_all('section', class_='fw-category-wrapper')
print(f'Found {len(sections)} category sections\n')

# Look at first category section structure
if sections:
    first_section = sections[0]
    print("First category section structure:")
    print("="*80)

    # Find heading elements
    h2 = first_section.find('h2')
    h3 = first_section.find('h3')
    h4 = first_section.find('h4')

    if h2:
        print(f"H2: classes={h2.get('class', [])}, text={h2.get_text(strip=True)}")
        link = h2.find('a')
        if link:
            print(f"  Link href: {link['href']}")

    if h3:
        print(f"H3: classes={h3.get('class', [])}, text={h3.get_text(strip=True)}")

    if h4:
        print(f"H4: classes={h4.get('class', [])}, text={h4.get_text(strip=True)}")

    # Look for any links in the section
    all_links = first_section.find_all('a', limit=3)
    print(f"\nFirst 3 links in section:")
    for i, link in enumerate(all_links):
        print(f"  {i}: {link.get_text(strip=True)[:60]} -> {link.get('href', 'NO HREF')}")
