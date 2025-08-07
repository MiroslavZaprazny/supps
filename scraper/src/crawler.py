import requests
import logging
from discovery import ProductDiscovery, BrainMarketProductDiscovery
from brand import BrandConfig, Brand
from db import Db 
import os
from models import Product
from sqlalchemy.orm import Session

PRODUCT_BATCH_SIZE = 20

class Crawler:
    def __init__(
            self,
            brand_config: BrandConfig,
            product_discovery: ProductDiscovery,
            db: Db
        ):
        self._brand_config = brand_config
        self._product_discovery = product_discovery
        self._db = db

    def crawl(self):
        # todo run concurrently??
        for category_page_url in self._brand_config.category_page_urls:
            try:
                res = requests.get(category_page_url)
                if res.status_code != 200:
                    logging.error(f"Request with uri {category_page_url} was not successful")
                    return

                batch: list[Product] = []
                with Session(self._db.engine()) as session:
                    for product_url in self._product_discovery.parse_product_urls_from_listing_page(res.text):
                        res = requests.get(product_url)
                        if res.status_code != 200:
                            logging.error(f"Request with uri {category_page_url} was not successful")
                            continue

                        product = self._product_discovery.parse_product(res.text)
                        batch.append(product)

                        if (len(batch) == PRODUCT_BATCH_SIZE):
                            session.add_all(batch)
                            session.commit()
                            batch = []

                    session.commit()


            except ConnectionError as e:
                logging.error(f"Request with uri {category_page_url} failed with error: {e}")

class CrawlerFactory:
    def get_crawler(self, brand: Brand) -> Crawler:
        match brand:
            case Brand.BRAINMARKET:
                return Crawler(BrandConfig(brand), BrainMarketProductDiscovery(), Db(os.environ['DATABASE_URL']))
            case _:
                raise Exception(f"Unimplemented site {site} crawler")