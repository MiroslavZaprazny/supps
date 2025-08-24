import requests
import logging
from parser import SiteParser, BrainMarketSiteParser
from brand import BrandConfig, Brand
from db import Db 
import os
from models import Product
from sqlalchemy.orm import Session

class Crawler:
    def __init__(
            self,
            brand_config: BrandConfig,
            site_parser: SiteParser,
            db: Db
        ):
        self._brand_config = brand_config
        self._site_parser = site_parser
        self._db = db

    def _get_product_detail_urls_from_listing_page(self, url: str) -> list[str]:
        urls: list[str] = []

        try:
            res = requests.get(url)
            if res.status_code != 200:
                raise Exception(f"Request with uri {url} was not successful")
        except requests.RequestException as e:
            logging.error(f"Request with uri {url} failed with error: {repr(e)}")
            return []

        #TODO: I dont really like that we only return a partial path would much rather to return the full urls
        urls.extend([f"{self._brand_config.base_url}/{product_page_url}" for product_page_url in self._site_parser.parse_product_detail_paths_from_listing_page(res.text)])

        #TODO: I dont really like that we only return a partial path would much rather to return the full urls
        paginated_product_listing_urls = [f"{url}/{paginated_listing_url}" for paginated_listing_url in self._site_parser.parse_paginated_product_listing_paths(res.text)]

        # todo run concurrently??
        for product_listing_page_url in paginated_product_listing_urls:
            try:
                res = requests.get(product_listing_page_url)
                if res.status_code != 200:
                    raise Exception(f"Request with uri {url} was not successful")

                #TODO: I dont really like that we only return a partial path would much rather to return the full urls
                urls.extend([f"{self._brand_config.base_url}/{product_page_url}" for product_page_url in self._site_parser.parse_product_detail_paths_from_listing_page(res.text)])
            except requests.RequestException as e:
                logging.error(f"Request failed with error: {str(e)}")
                continue

        return urls

    def _crawl_product_detail_pages(self, urls: list[str]) -> list[Product]:
        products: list[Product] = []

        # todo run concurrently??
        for url in urls:
            res = requests.get(url)

            if res.status_code != 200:
                logging.error(f"Request with uri {url} was not successful")

            try:
                product = self._site_parser.parse_product(res.text)
                product.add_url(url)
                products.append(product)
            except Exception as e:
                logging.error(f"Failed to parse product with error {repr(e)}")
                continue

        return products

    def crawl(self):
        for product_listing_url in self._brand_config.product_listing_urls:
            product_detail_urls = self._get_product_detail_urls_from_listing_page(product_listing_url)
            batch = [product_detail_urls[i:i + 100] for i in range(0, len(product_detail_urls), 100)]

            for urls in batch:
                with Session(self._db.engine()) as session:
                    session.add_all(self._crawl_product_detail_pages(urls))
                    session.commit()

class CrawlerFactory:
    def get_crawler(self, brand: Brand) -> Crawler:
        match brand:
            case Brand.BRAINMARKET:
                return Crawler(BrandConfig(brand), BrainMarketSiteParser(), Db(os.environ['DATABASE_URL']))
            case _:
                raise Exception(f"Unimplemented site {site} crawler")
