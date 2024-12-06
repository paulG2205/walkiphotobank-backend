import os
import shutil
from elasticsearch import Elasticsearch
from pinscrape import scraper, Pinterest
import requests
from bs4 import BeautifulSoup

# Configuration
proxies = {}
number_of_workers = 10
images_to_download = 4

es = Elasticsearch(
    hosts=["http://localhost:9200"],
    http_auth=("elastic", "cB7AAT0k")  
)

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
    
    
    
COLORS = [
    "black", "white", "red", "blue", "green", "yellow", "purple", 
    "pink", "orange", "gray", "brown", "teal", "cyan", "magenta", 
    "gold", "silver", "beige", "ivory", "maroon", "navy", "olive", 
    "lime", "coral", "peach", "violet", "turquoise", "indigo", 
    "lavender", "charcoal", "chocolate", "tan", "amber", "emerald", 
    "ruby", "sapphire", "rose", "aquamarine", "burgundy", "plum"
]

def run_scraper_and_save(q: str):
    """
    Ejecuta el scrapper y guarda los resultados en Elasticsearch.
    Asegura que el keyword completo se almacene correctamente.
    """
    try:
        # Ejecutar scrapers
        search_engine_urls = using_search_engine(q)
        pinterest_urls = using_pinterest_apis(q)
        all_urls = search_engine_urls + pinterest_urls

        index_name = "photos"
        for url in all_urls:
            es.index(
                index=index_name,
                body={
                    "url": url,
                    "keyword": q.lower(),  # Asegura que almacene exactamente lo que se busca
                    "source": "scraper",
                    "timestamp": "now"
                }
            )
        print(f"Scraping completed and data indexed for query: {q}")
    except Exception as e:
        print(f"Error in background scraper task: {e}")