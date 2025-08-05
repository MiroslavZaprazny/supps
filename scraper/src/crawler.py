import requests
import logging
from discovery import ProductDiscovery, BrainMarketProductDiscovery
from sites import SiteConfig, Site

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

class CrawlerFactory:
    def get_crawler(self, site: Site) -> Crawler:
        match site:
            case Site.BRAINMARKET:
                return Crawler(SiteConfig(site), BrainMarketProductDiscovery())
            case _:
                raise Exception(f"Unimplemented site {site} crawler")