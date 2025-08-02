import logging
from elasticsearch import Elasticsearch
from datetime import datetime

class ElasticsearchHandler(logging.Handler):
    def __init__(self, host: str, idx: str = 'scraper'):
        super().__init__()
        self.inner = Elasticsearch([host])
        self.idx = idx

    def emit(self, record: logging.LogRecord) -> None:
        log_entry: dict[str, str|int] = {
            'timestamp': datetime.now().isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'funcName': record.funcName,
            'lineno': record.lineno
        }
        
        try:
            self.inner.index(
                index=f"{self.idx}-{datetime.now().strftime('%Y-%m')}",
                body=log_entry
            )
        except Exception as e:
            print(f"Failed to log to Elasticsearch: {e}")

def init_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    es_handler = ElasticsearchHandler('http://localhost:9200')
    logger.addHandler(es_handler)

    logger.info("Halo funguje to?")
