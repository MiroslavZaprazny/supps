from logger import init_logger
import sys
from crawler import Site, CrawlerFactory

if __name__ == "__main__":
    args = sys.argv
    print(args)
    if len(args) < 2:
        print(f"Specify a site to crawl, available options are {list(Site)}")
        exit(1)

    try:
        site = Site(args[1])
    except ValueError:
        print(f"Site {args[1]} is not supported available options are {list(Site)}")
        exit(1)

    init_logger()

    CrawlerFactory().get_crawler(site).crawl()