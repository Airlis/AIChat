import requests
from bs4 import BeautifulSoup

def scrape_content(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        # Extract text from HTML
        content = extract_text(response.text)

        # Get 'Last-Modified' and 'ETag' headers
        last_modified = response.headers.get('Last-Modified')
        etag = response.headers.get('ETag')

        return content, last_modified, etag
    except Exception as e:
        print(f"Error scraping content from {url}: {e}")
        return None, None, None

def extract_text(html):
    soup = BeautifulSoup(html, 'html.parser')
    for script_or_style in soup(['script', 'style']):
        script_or_style.decompose()
    text = ' '.join(soup.stripped_strings)
    return text
