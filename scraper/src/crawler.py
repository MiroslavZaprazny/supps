import requests
import logging
from discovery import ProductDiscovery, BrainMarketProductDiscovery
from brand import BrandConfig, Brand

class Crawler:
    def __init__(self, brand_config: BrandConfig, product_discovery: ProductDiscovery):
        self._brand_config = brand_config
        self._product_discovery = product_discovery

    def crawl(self):
        # todo run concurrently
        for category_page_url in self._brand_config.category_page_urls:
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

class CrawlerFactory:
    def get_crawler(self, brand: Brand) -> Crawler:
        match brand:
            case Brand.BRAINMARKET:
                return Crawler(BrandConfig(brand), BrainMarketProductDiscovery())
            case _:
                raise Exception(f"Unimplemented site {site} crawler")