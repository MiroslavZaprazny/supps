from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase
from sqlalchemy import  Integer, String, DateTime, DECIMAL
from datetime import datetime
from decimal import Decimal

class Base(DeclarativeBase):
    pass

class Product(Base):
    __tablename__ = 'product_page'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    marketing_name: Mapped[str] = mapped_column(String(255))
    quantity: Mapped[int] = mapped_column(Integer())
    price: Mapped[Decimal] = mapped_column(DECIMAL(10, 2))
    created_at: Mapped[datetime] = mapped_column(DateTime())

    def __init__(self, name: str, marketing_name: str, quantity: int, price: Decimal):
        self.name = name
        self.quantity = quantity
        self.price = price
        self.created_at = datetime.now()
        self.marketing_name = marketing_name
