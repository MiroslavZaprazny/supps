from abc import ABC, abstractmethod
from models import Product
from decimal import Decimal
from datetime import datetime
from bs4 import BeautifulSoup

class SiteParser(ABC):
    @abstractmethod
    def parse_paginated_product_listing_links(self, page_content: str) -> list[str]:
        pass

    @abstractmethod
    def parse_product_detail_urls_from_listing_page(self, page_content: str) -> list[str]:
        pass

    @abstractmethod
    def parse_product(self, page_content: str) -> Product:
        pass

class BrainMarketSiteParser(SiteParser):
    def parse_paginated_product_listing_links(self, page_content: str) -> list[str]:
        # parser = BeautifulSoup(page_content, features='html.parser')
        # pagination_div = parser.find(class_='pagination')
        # for child in pagination_div.children:

        # last_page_number = pagination_div.children
        return []

    def parse_product_detail_urls_from_listing_page(self, page_content: str) -> list[str]:
        parser = BeautifulSoup(page_content, features='html.parser')
        products_div = parser.find(class_ = 'products')
        links: list[str] = []

        print(type(products_div))
        exit(1)
        for product in products_div.find_all(class_='product'): #type: ignore
            links.append(product.find('a').attrs['href']) #type: ignore

        return links

    def parse_product(self, page_content: str) -> Product:
        # todo
        return Product(
            name='BrainMax sleep magnesium',
            quantity=100,
            price=Decimal('28.35'),
            created_at=datetime.now()
        )