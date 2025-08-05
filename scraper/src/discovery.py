from abc import ABC, abstractmethod

class ProductDiscovery(ABC):
    @abstractmethod
    def get_product_urls_from_listing_page(self, page_content: str) -> list[str]:
        pass

class BrainMarketProductDiscovery(ProductDiscovery):
    def get_product_urls_from_listing_page(self, page_content: str) -> list[str]:
        return []