from pydantic import BaseModel

from model.item import Item


class FavoriteItemResponse(BaseModel):
    item: Item
