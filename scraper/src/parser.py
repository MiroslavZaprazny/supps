from abc import ABC, abstractmethod
from models import Product
from decimal import Decimal
from bs4 import BeautifulSoup, Tag
import re

class SiteParser(ABC):
    @abstractmethod
    def parse_paginated_product_listing_paths(self, page_content: str) -> list[str]:
        pass

    @abstractmethod
    def parse_product_detail_paths_from_listing_page(self, page_content: str) -> list[str]:
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

    def parse_product_detail_paths_from_listing_page(self, page_content: str) -> list[str]:
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

        return Product(
            name=name,
            marketing_name= self._generate_marketing_name(name),
            quantity=self._parse_quanitity(name),
            price=self._parse_product_price(parser),
        )

    def _parse_product_price(self, parser: BeautifulSoup) -> Decimal:
        price_tag = parser.find(class_='price-final-holder')
        assert isinstance(price_tag, Tag)

        contents = price_tag.text
        assert isinstance(contents, str)
        contents = contents.strip()

        return Decimal(contents[contents.find('€')+1:].replace(',', '.'))


    def _parse_product_name(self, parser: BeautifulSoup) -> str:
        heading_div = parser.find(class_='p-detail-inner-header')
        assert isinstance(heading_div, Tag)

        return next(heading_div.stripped_strings)

    """
        Some products can have additional info in the name, for eg.

        "BrainMax Sleep Magnesium, 320 mg, 100 kapsúl (Horčík, GABA, L-theanin, Vitamín B6, šťava z višne)"
        or "BrainMax Berberin 500 mg, 90 rastlinných kapsúl"

        When parsing the title we look for 3 things:
            - a dot
            - capsule count
            - grammage count

        We then slice the title by the first occurrence of either of those
        So in the examples given above we will return "BrainMax Sleep Magnesium" and "BrainMax Berberin"
    """
    def _generate_marketing_name(self, title: str) -> str:
        sub = title.find(',')
        if sub == -1:
            return title
       
        terminators = [sub]

        capsule_match = re.search(r'(\d+)\s+(?:\w+\s+)?kapsúl', title)
        if capsule_match:
            terminators.append(capsule_match.start())

        grammage_match = re.search(r'(\d+)\s+(?:ml|mg|g)', title)
        if grammage_match:
            terminators.append(grammage_match.start())

        return title[:min(terminators)]

    """
        Some products can have the quantity specified in the title which we can take advatage of for eg. 

        BrainMax Sleep Magnesium, 320 mg, 100 kapsúl (Horčík, GABA, L-theanin, Vitamín B6, šťava z višne)

        We prioritize the num of capsules over the grammage/volume, if they are both present
    """
    def _parse_quanitity(self, title: str) -> int:
        capsule_match = re.search(r'(\d+)\s+(?:\w+\s+)?kapsúl', title)
        if capsule_match:
            return int(capsule_match.group(1))

        grammage_match = re.search(r'(\d+)\s+(?:ml|mg|g)', title)
        if grammage_match:
            return int(grammage_match.group(1))

        raise Exception(f"Unable to parse quantity for product with title {title}")
