from abc import ABC, abstractmethod
import requests
import logging

class ProductDiscovery(ABC):
    @abstractmethod
    def get_product_urls_from_listing_page(self, page_content: str) -> list[str]:
        pass

class BrainMarketProductDiscovery(ProductDiscovery):
    def get_product_urls_from_listing_page(self, page_content: str) -> list[str]:
        return []

class SiteConfig:
    def __init__(self, base_url: str, category_page_urls: list[str]):
        self.base_url = base_url
        self.category_page_urls: list[str] = []

        for category_page_url in category_page_urls:
            self.category_page_urls.append(f"{base_url}{category_page_url}")

class Crawler:
    def __init__(self, site_config: SiteConfig, product_discovery: ProductDiscovery):
        self._site_config = site_config
        self._product_discovery = product_discovery

    def crawl(self):
        # todo run concurrently
        for category_page_url in self._site_config.category_page_urls:
            try:
                res = requests.get(category_page_url)
                if res.status_code != 200:
                    logging.error(f"Request with uri {category_page_url} was not successful")
                    return

                for product_url in self._product_discovery.get_product_urls_from_listing_page(res.text):
                    res = requests.get(product_url)
                    if res.status_code != 200:
                        logging.error(f"Request with uri {category_page_url} was not successful")

            except ConnectionError as e:
                logging.error(f"Request with uri {category_page_url} failed with error: {e}")