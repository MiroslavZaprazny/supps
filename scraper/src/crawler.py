import requests
import logging
from discovery import SiteParser, BrainMarketSiteParser
from brand import BrandConfig, Brand
from db import Db 
import os
from models import Product

PRODUCT_BATCH_SIZE = 20

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

    # Returns a list of individual product page urls based from a product listing page
    def _crawl_listing_page(self, url: str) -> tuple[requests.Response, list[str]]:
        res = requests.get(url)
        if res.status_code != 200:
            raise Exception(f"Request with uri {url} was not successful")

        return (res, self._site_parser.parse_product_detail_urls_from_listing_page(res.text))

    def _crawl_product_detail_pages(self, urls: list[str]) -> list[Product]:
        products: list[Product] = []

        for url in urls:
            res = requests.get(url)
            if res.status_code != 200:
                logging.error(f"Request with uri {url} was not successful")

            products.append(self._site_parser.parse_product(res.text))

        return products

    def crawl(self):
        # todo run concurrently??
        for category_page_url in self._brand_config.category_page_urls:
            try:
                category_page_res, product_page_urls = self._crawl_listing_page(category_page_url)
                products = self._crawl_product_detail_pages(product_page_urls)
            except Exception as e:
                logging.error(f"Request with uri {category_page_url} failed with error: {e}")
                continue

            for product_listing_page_url in self._site_parser.parse_paginated_product_listing_links(category_page_res.text):
                category_page_res, product_page_urls = self._crawl_listing_page(product_listing_page_url)
                products = self._crawl_product_detail_pages(product_page_urls)
            #todo save products


class CrawlerFactory:
    def get_crawler(self, brand: Brand) -> Crawler:
        match brand:
            case Brand.BRAINMARKET:
                return Crawler(BrandConfig(brand), BrainMarketSiteParser(), Db(os.environ['DATABASE_URL']))
            case _:
                raise Exception(f"Unimplemented site {site} crawler")