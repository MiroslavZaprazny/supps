from enum import Enum
import yaml

class Site(Enum):
    BRAINMARKET = 'brainmarket'

class SiteConfig:
    def __init__(self, site: Site):
        config = load_site_config(site)

        self.base_url = config['base_url']
        self.category_page_urls: list[str] = [f"{self.base_url}{category_page_url}" for category_page_url in config['category_page_urls']]


def load_site_config(site: Site) -> dict[str, str]:
    match site:
        case Site.BRAINMARKET:
            with open('config/sites/brainmarket.yml') as file:
                return yaml.safe_load(file)
        case _:
            raise Exception(f"Site config not implement for {site}")
