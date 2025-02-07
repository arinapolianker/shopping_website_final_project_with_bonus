from typing import Optional,Dict
from pydantic import BaseModel

from model.order_status import OrderStatus


class OrderRequest(BaseModel):
    id: Optional[int] = None
    user_id: int
    shipping_address: str
    item_quantities: Dict[int, int]
    total_price: float
    status: OrderStatus
