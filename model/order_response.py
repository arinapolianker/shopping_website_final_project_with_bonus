from datetime import date
from typing import List

from pydantic import BaseModel

from model.order_item_detail import OrderItemDetail
from model.order_status import OrderStatus


class OrderResponse(BaseModel):
    id: int
    item: List[OrderItemDetail]
    total_price: float
    shipping_address: str
    order_date: date
    status: OrderStatus
