from typing import Optional, List

from model.favorite_item import FavoriteItem
from model.favorite_item_request import FavoriteItemRequest
from model.favorite_item_response import FavoriteItemResponse
from repository import favorite_item_repository
from service import user_service, item_service


async def get_by_id(favorite_item_id: int) -> Optional[FavoriteItem]:
    return await favorite_item_repository.get_by_id(favorite_item_id)


async def get_favorite_items_by_user_id(user_id: int) -> List[FavoriteItemResponse]:
    favorite_items = await favorite_item_repository.get_favorite_items_by_user_id(user_id)
    if favorite_items is not None:
        response = [
            FavoriteItemResponse(
                item=(await item_service.get_item_by_id(favorite_item.item_id))
            )
            for favorite_item in favorite_items
        ]
        return response


async def get_all_favorite_items() -> List[FavoriteItem]:
    return await favorite_item_repository.get_all_favorite_items()


async def create_favorite_item(favorite_item_request: FavoriteItemRequest) -> Optional[int]:
    user = await user_service.get_user_by_id(favorite_item_request.user_id)
    if user is not None:
        item_id = favorite_item_request.item_id
        existing_favorite = await favorite_item_repository.get_favorite_item_by_user_and_item(
            user_id=user.id,
            item_id=item_id
        )
        if existing_favorite:
            raise ValueError("This item is already in your favorite list.")
        favorite_item = FavoriteItem(user_id=user.id, item_id=item_id)
        return await favorite_item_repository.create_favorite_item(favorite_item)
    return None


async def update_favorite_items(favorite_item_id: int, favorite_item: FavoriteItem):
    await favorite_item_repository.update_favorite_items(favorite_item_id, favorite_item)


async def delete_by_id(favorite_item_id: int):
    await favorite_item_repository.delete_by_id(favorite_item_id)


async def delete_by_user_and_item_id(user_id: int, item_id: int):
    await favorite_item_repository.delete_by_user_and_item_id(user_id, item_id)
