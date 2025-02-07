from pydantic import BaseModel


class OrderItemDetail(BaseModel):
    item_id: int
    name: str
    price: float
    quantity: int
    item_stock: int
