from abc import ABC, abstractmethod
from models import Product
from decimal import Decimal
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
        parser = BeautifulSoup(page_content, features='html.parser')
        name = self._parse_product_name(parser).strip()
        print(f"name: {name}")

        product =  Product(
            name=name,
            marketing_name= self._generate_marketing_name(name),
            quantity=100,
            price=Decimal(self._parse_product_price(parser)),
        )

        print(repr(product))

        return product

    def _parse_product_price(self, parser: BeautifulSoup) -> str:
        price_tag = parser.find(class_='price-final-holder')
        assert isinstance(price_tag, Tag)

        contents = price_tag.text
        assert isinstance(contents, str)
        contents = contents.strip()

        return contents[contents.find('€')+1:]


    def _parse_product_name(self, parser: BeautifulSoup) -> str:
        heading_div = parser.find(class_='p-detail-inner-header')
        assert isinstance(heading_div, Tag)

        return next(heading_div.stripped_strings)

    """
        Some products can have additional info in the name, for eg.

        BrainMax Sleep Magnesium, 320 mg, 100 kapsúl (Horčík, GABA, L-theanin, Vitamín B6, šťava z višne)

        We try to parse the string so that we can have some short pretty name instead of a looooong detailed one
    """
    def _generate_marketing_name(self, full_name: str) -> str:
        sub = full_name.find(',')
        if sub == -1:
            return full_name

        return full_name[:sub]

    """
        Some products can have additional info in the name, for eg.

        BrainMax Sleep Magnesium, 320 mg, 100 kapsúl (Horčík, GABA, L-theanin, Vitamín B6, šťava z višne)

        We try to parse the string and retrieve the quantity for the title 
    """
    # def _parse_quanitity(self, full_name: str) -> str:
    #     sub = full_name.find(',')
    #     if sub == -1:
    #         return full_name

    #     return full_name[:sub]

