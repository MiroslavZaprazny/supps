from logger import init_logger
import sys
from crawler import CrawlerFactory
from brand import Brand
import asyncio

if __name__ == "__main__":
    args = sys.argv
    print(args)
    if len(args) < 2:
        print(f"Specify a brand to crawl, available options are {list(Brand)}")
        exit(1)

    try:
        brand = Brand(args[1])
    except ValueError:
        print(f"Brand {args[1]} is not supported, available options are {list(Brand)}")
        exit(1)

    init_logger()

    asyncio.run(CrawlerFactory().get_crawler(brand).crawl())