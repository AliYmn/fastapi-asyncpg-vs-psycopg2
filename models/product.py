from sqlalchemy import Column, Float, String, Text

from models.base import BaseModel


class Product(BaseModel):
    __tablename__ = "products"

    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    sku = Column(String, unique=True, index=True)
