from pydantic import BaseModel


class OrderItemQuantity(BaseModel):
    user_id: int
    item_id: int
    quantity: int
