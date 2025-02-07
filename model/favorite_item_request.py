from pydantic import BaseModel


class FavoriteItemRequest(BaseModel):
    user_id: int
    item_id: int
