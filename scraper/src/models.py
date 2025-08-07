from sqlalchemy.orm import declarative_base, mapped_column, Mapped
from sqlalchemy import Column, Integer, String, DateTime, DECIMAL
from datetime import datetime

Base = declarative_base()
class Product(Base):
    __table__name = 'product_page'

    id: Mapped[int] = mapped_column(Column(Integer, primary_key=True))
    name: Mapped[str] = mapped_column(Column(String))
    quantity: Mapped[int] = mapped_column(Column(Integer))
    price: Mapped[str] = mapped_column(DECIMAL(10, 2))
    created_at: Mapped[datetime] = mapped_column(Column(DateTime))
