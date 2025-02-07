from typing import Optional

from pydantic import BaseModel, condecimal


class Item(BaseModel):
    id: Optional[int] = None
    name: str
    price: condecimal(max_digits=10, decimal_places=2)
    item_stock: int
