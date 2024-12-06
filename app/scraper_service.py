import os
import shutil
from pinscrape import scraper, Pinterest
import requests
from bs4 import BeautifulSoup

# Configuration
proxies = {}
number_of_workers = 10
images_to_download = 4

def using_search_engine(keyword: str):
    """
    Scrape using the search engine with a dynamic keyword and return direct image URLs.
    """
    try:
        details = scraper.scrape(keyword, "", proxies, number_of_workers, images_to_download)
        page_urls = details.get("extracted_urls", [])
        
        image_urls = []
        for page_url in page_urls:
            try:
                response = requests.get(page_url, proxies=proxies, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    # Extract all <img> tags
                    img_tags = soup.find_all('img')
                    # Filter for valid image URLs
                    for img in img_tags:
                        src = img.get('src')
                        if src and src.startswith(('http://', 'https://')):
                            image_urls.append(src)
            except Exception as e:
                pass
        

        if os.path.exists(keyword):
            shutil.rmtree(keyword)
        
        return image_urls
    except Exception as e:
        if os.path.exists(keyword):
            shutil.rmtree(keyword)
        raise RuntimeError(f"Error during search engine scraping: {e}")

def using_pinterest_apis(keyword: str):
    """
    Scrape using Pinterest APIs with a dynamic keyword and return direct image URLs.
    """
    try:
        p = Pinterest(proxies=proxies)
        page_urls = p.search(keyword, images_to_download)
        
        image_urls = []
        for page_url in page_urls:
            try:
                response = requests.get(page_url, proxies=proxies, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    img_tags = soup.find_all('img')
                    for img in img_tags:
                        src = img.get('src')
                        if src and src.startswith(('http://', 'https://')):
                            image_urls.append(src)
            except Exception as e:
                pass
        
        if os.path.exists(keyword):
            shutil.rmtree(keyword)
        
        return image_urls
    except Exception as e:
        if os.path.exists(keyword):
            shutil.rmtree(keyword)
        raise RuntimeError(f"Error during Pinterest API scraping: {e}")