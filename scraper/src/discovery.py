from abc import ABC, abstractmethod
from models import Product
from decimal import Decimal
from datetime import datetime
from bs4 import BeautifulSoup, Tag

class SiteParser(ABC):
    @abstractmethod
    def parse_paginated_product_listing_paths(self, page_content: str) -> list[str]:
        pass

    @abstractmethod
    def parse_product_detail_urls_from_listing_page(self, page_content: str) -> list[str]:
        pass

    @abstractmethod
    def parse_product(self, page_content: str) -> Product:
        pass

class BrainMarketSiteParser(SiteParser):
    def parse_paginated_product_listing_paths(self, page_content: str) -> list[str]:
        parser = BeautifulSoup(page_content, features='html.parser')
        pagination_div = parser.find(class_='pagination')
        assert isinstance(pagination_div, Tag)

        last_page_element = parser.find(attrs={'data-testid': 'linkLastPage'})
        assert isinstance(last_page_element, Tag)
        last_page_num = int(last_page_element.text)

        return [f"strana-{num}" for num in range(2, last_page_num+1)]

    def parse_product_detail_urls_from_listing_page(self, page_content: str) -> list[str]:
        parser = BeautifulSoup(page_content, features='html.parser')
        products_div = parser.find(class_ = 'products')
        links: list[str] = []

        assert isinstance(products_div, Tag)
        for product in products_div.find_all(class_='product'):
            assert isinstance(product, Tag)

            product_link = product.find('a')
            assert isinstance(product_link, Tag)

            links.append(str(product_link.attrs['href']))

        return links

    def parse_product(self, page_content: str) -> Product:
        # todo
        return Product(
            name='BrainMax sleep magnesium',
            quantity=100,
            price=Decimal('28.35'),
            created_at=datetime.now()
        )