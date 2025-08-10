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

    # Returns a list of individual product page urls based on a product listing page
    def _crawl_listing_page(self, url: str) -> tuple[requests.Response, list[str]]:
        res = requests.get(url)
        if res.status_code != 200:
            raise Exception(f"Request with uri {url} was not successful")

        return (res, self._site_parser.parse_product_detail_urls_from_listing_page(res.text))

    def _crawl_product_detail_pages(self, urls: list[str]) -> list[Product]:
        products: list[Product] = []

        # todo run concurrently??
        for url in urls:
            res = requests.get(url)

            if res.status_code != 200:
                logging.error(f"Request with uri {url} was not successful")

            products.append(self._site_parser.parse_product(res.text))

        return products

    def _crawl_category_page(self, url: str) -> list[Product]:
        products: list[Product] = []

        try:
            category_page_res, product_page_urls = self._crawl_listing_page(url)

            #TODO: I dont really like that we only return a partial path would much rather to return the full urls
            product_page_urls = [f"{self._brand_config.base_url}/{product_page_url}" for product_page_url in product_page_urls]
            products.extend(self._crawl_product_detail_pages(product_page_urls))
        except Exception as e:
            logging.error(f"Request with uri {url} failed with error: {e}")

            return products


        #TODO: I dont really like that we only return a partial path would much rather to return the full urls
        paginated_product_listing_urls = [f"{url}/{url}" for url in self._site_parser.parse_paginated_product_listing_paths(category_page_res.text)]
        print(paginated_product_listing_urls)

        for product_listing_page_url in paginated_product_listing_urls:
            try:
                _, product_page_urls = self._crawl_listing_page(product_listing_page_url)

                #TODO: I dont really like that we only return a partial path would much rather to return the full urls
                product_page_urls = [f"{self._brand_config.base_url}/{product_page_url}" for product_page_url in product_page_urls]
                products.extend(self._crawl_product_detail_pages(product_page_urls))
            except Exception as e:
                logging.error(f"Request failed with error: {e}")
                continue

        return products


    def crawl(self):
        for category_page_url in self._brand_config.category_page_urls:
            #todo save products
            products = self._crawl_category_page(category_page_url)


class CrawlerFactory:
    def get_crawler(self, brand: Brand) -> Crawler:
        match brand:
            case Brand.BRAINMARKET:
                return Crawler(BrandConfig(brand), BrainMarketSiteParser(), Db(os.environ['DATABASE_URL']))
            case _:
                raise Exception(f"Unimplemented site {site} crawler")