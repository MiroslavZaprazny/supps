from abc import ABC, abstractmethod
from models import Product
from decimal import Decimal
from datetime import datetime

class ProductDiscovery(ABC):
    @abstractmethod
    def parse_product_urls_from_listing_page(self, page_content: str) -> list[str]:
        pass

    @abstractmethod
    def parse_product(self, page_content: str) -> Product:
        pass

class BrainMarketProductDiscovery(ProductDiscovery):
    def parse_product_urls_from_listing_page(self, page_content: str) -> list[str]:
        # todo
        return ['https://www.brainmarket.cz/brainmax-sleep-magnesium-320-mg-100-kapsli/']

    def parse_product(self, page_content: str) -> Product:
        # todo
        return Product(
            name='BrainMax sleep magnesium',
            quantity=100,
            price=Decimal('28.35'),
            created_at=datetime.now()
        )