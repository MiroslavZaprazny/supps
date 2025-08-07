from sqlalchemy.orm import declarative_base, mapped_column, Mapped
from sqlalchemy import  Integer, String, DateTime, DECIMAL
from datetime import datetime

Base = declarative_base()
class Product(Base):
    __tablename__ = 'product_page'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    quantity: Mapped[int] = mapped_column(Integer())
    price: Mapped[str] = mapped_column(DECIMAL(10, 2))
    created_at: Mapped[datetime] = mapped_column(DateTime())
