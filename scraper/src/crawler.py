import logging
from parser import SiteParser, BrainMarketSiteParser
from brand import BrandConfig, Brand
from db import Db 
import os
from models import Product
from sqlalchemy.orm import Session
import asyncio
import aiohttp

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

    async def _fetch_contents(self, session: aiohttp.ClientSession, url: str) -> str:
        async with session.get(url) as res:
            return await res.text()

    async def _crawl_listing_page(self, url: str) -> list[str]:
        product_detail_urls: list[str] = []

        async with  aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15)) as session:
            contents = await self._fetch_contents(session, url)

            #TODO: I dont really like that we only return a partial path would much rather to return the full urls
            product_detail_urls.extend([f"{self._brand_config.base_url}/{product_page_url}" for product_page_url in self._site_parser.parse_product_detail_paths_from_listing_page(contents)])

            #TODO: I dont really like that we only return a partial path would much rather to return the full urls
            paginated_product_listing_urls = [f"{url}/{paginated_listing_url}" for paginated_listing_url in self._site_parser.parse_paginated_product_listing_paths(contents)]
            tasks = [self._fetch_contents(session, url) for url in paginated_product_listing_urls]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, Exception):
                    logging.error(f"Request failed with error {repr(result)}")
                    continue

                assert isinstance(result, str)
                product_detail_urls.extend([f"{self._brand_config.base_url}/{product_page_url}" for product_page_url in self._site_parser.parse_product_detail_paths_from_listing_page(result)])

        return product_detail_urls

    async def _parse_product_from_detail_page(self, session: aiohttp.ClientSession, url: str) -> Product:
        async with session.get(url) as res:
            content = await res.text()
            product = self._site_parser.parse_product(content)
            product.add_url(url)

            return product

    async def _crawl_product_detail_pages(self, urls: list[str]) -> list[Product]:
        products: list[Product] = []

        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15)) as session:
            tasks = [self._parse_product_from_detail_page(session, url) for url in urls]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in results:
                if isinstance(result, Exception):
                    logging.error(f"Failed to parse product with error {repr(result)}")
                    continue

                assert isinstance(result, Product)
                products.append(result)

        return products

    async def crawl(self):
        for product_listing_url in self._brand_config.product_listing_urls:
            product_detail_urls = await self._crawl_listing_page(product_listing_url)
            batch = [product_detail_urls[i:i + 100] for i in range(0, len(product_detail_urls), 100)]

            for urls in batch:
                with Session(self._db.engine()) as session:
                    products = await self._crawl_product_detail_pages(urls)
                    session.add_all(products)
                    session.commit()

class CrawlerFactory:
    def get_crawler(self, brand: Brand) -> Crawler:
        match brand:
            case Brand.BRAINMARKET:
                return Crawler(BrandConfig(brand), BrainMarketSiteParser(), Db(os.environ['DATABASE_URL']))
            case _:
                raise Exception(f"Unimplemented site {brand} crawler")
