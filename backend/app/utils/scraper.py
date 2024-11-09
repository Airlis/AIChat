import requests
from bs4 import BeautifulSoup
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class WebScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; VisitorClassifier/1.0)'
        }

    def scrape_content(self, url: str) -> Dict:
        """Scrape website content and structure it"""
        try:
            # Add http:// if not present
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            logger.info(f"Scraping URL: {url}")
            
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            logger.info(f"Response status: {response.status_code}")
            logger.info(f"Response encoding: {response.encoding}")
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for element in soup(['script', 'style', 'nav', 'footer']):
                element.decompose()
            
            # Extract main content sections
            sections = []
            for section in soup.find_all(['article', 'section', 'div']):
                text = section.get_text(strip=True)
                if len(text) > 100:  # Only keep substantial sections
                    sections.append({
                        'text': text,
                        'html': str(section)
                    })
            
            logger.info(f"Found {len(sections)} content sections")
            if not sections:
                logger.warning("No content sections found")
            
            result = {
                'url': url,
                'title': soup.title.string if soup.title else '',
                'sections': sections
            }
            
            logger.info(f"Scraping complete. Title: {result['title']}")
            return result

        except requests.RequestException as e:
            logger.error(f"Request error for {url}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Scraping error for {url}: {str(e)}")
            raise
