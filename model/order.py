from datetime import date
from typing import Optional

from pydantic import BaseModel

from model.order_status import OrderStatus


class Order(BaseModel):
    id: Optional[int] = None
    user_id: int
    order_date: date
    shipping_address: str
    total_price: float
    status: OrderStatus



