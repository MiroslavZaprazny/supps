from sqlalchemy import create_engine, Engine

class Db:
    def __init__(self, db_url: str) -> None:
        self._engine = None
        self._db_url = db_url

    def init(self):
        if self._engine is None:
            self._engine = create_engine(self._db_url)

    def engine(self) -> Engine:
        if self._engine is None:
            self.init()
        return self._engine # type: ignore
