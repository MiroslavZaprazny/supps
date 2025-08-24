import requests
import logging
from parser import SiteParser, BrainMarketSiteParser
from brand import BrandConfig, Brand
from db import Db 
import os
from models import Product
from sqlalchemy.orm import Session
import asyncio
import aiohttp

class ProductDetailCrawlResult:
    def __init__(self, err: Exception|None, product: Product|None):
        if err is None and product is None:
            raise Exception("Both error and product cannot be null")

        if err is not None and product is not None:
            raise Exception("Both error and product cannot be present at the same time")

        self.err = err
        self.product = product

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
        # paginated_product_listing_urls = [f"{url}/{paginated_listing_url}" for paginated_listing_url in self._site_parser.parse_paginated_product_listing_paths(res.text)]

        # todo run concurrently??
        # for product_listing_page_url in paginated_product_listing_urls:
        #     try:
        #         res = requests.get(product_listing_page_url)
        #         if res.status_code != 200:
        #             raise Exception(f"Request with uri {url} was not successful")

        #         #TODO: I dont really like that we only return a partial path would much rather to return the full urls
        #         urls.extend([f"{self._brand_config.base_url}/{product_page_url}" for product_page_url in self._site_parser.parse_product_detail_paths_from_listing_page(res.text)])
        #     except requests.RequestException as e:
        #         logging.error(f"Request failed with error: {str(e)}")
        #         continue

        return urls

    async def _parse_product_from_detail_page(self, session: aiohttp.ClientSession, url: str) -> ProductDetailCrawlResult:
        try:
            async with session.get(url) as res:
                content = await res.text()
                product = self._site_parser.parse_product(content)
                product.add_url(url)

            return ProductDetailCrawlResult(None, product)
        except Exception as e:
            return ProductDetailCrawlResult(e, None)

    async def _crawl_product_detail_pages(self, urls: list[str]) -> list[Product]:
        products: list[Product] = []
        results: list[ProductDetailCrawlResult] = []

        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15)) as session:
            tasks = [self._parse_product_from_detail_page(session, url) for url in urls]
            results = await asyncio.gather(*tasks)

        for result in results:
            if result.err is not None:
                logging.error(f"Failed to parse product with error {repr(result.err)}")
                continue
            elif result.product is not None:
                products.append(result.product)

        return products

    def crawl(self):
        for product_listing_url in self._brand_config.product_listing_urls:
            product_detail_urls = self._get_product_detail_urls_from_listing_page(product_listing_url)
            batch = [product_detail_urls[i:i + 100] for i in range(0, len(product_detail_urls), 100)]

            for urls in batch:
                with Session(self._db.engine()) as session:
                    products = asyncio.run(self._crawl_product_detail_pages(urls))
                    session.add_all(products)
                    session.commit()

class CrawlerFactory:
    def get_crawler(self, brand: Brand) -> Crawler:
        match brand:
            case Brand.BRAINMARKET:
                return Crawler(BrandConfig(brand), BrainMarketSiteParser(), Db(os.environ['DATABASE_URL']))
            case _:
                raise Exception(f"Unimplemented site {site} crawler")
