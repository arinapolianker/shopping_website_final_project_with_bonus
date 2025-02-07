from pydantic import BaseModel

from model.order_status import OrderStatus


class OrderClose(BaseModel):
    order_id: int
    user_id: int
    shipping_address: str
    status: OrderStatus
