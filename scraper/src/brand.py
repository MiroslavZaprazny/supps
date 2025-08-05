from enum import Enum
import yaml

class Brand(Enum):
    BRAINMARKET = 'brainmarket'

class BrandConfig:
    def __init__(self, brand: Brand):
        config = load_brand_config(brand)

        self.base_url = config['base_url']
        self.category_page_urls: list[str] = [f"{self.base_url}{category_page_url}" for category_page_url in config['category_page_urls']]


def load_brand_config(brand: Brand) -> dict[str, str]:
    match brand:
        case Brand.BRAINMARKET:
            with open('config/brands/brainmarket.yml') as file:
                return yaml.safe_load(file)
        case _:
            raise Exception(f"Site config not implement for {site}")
