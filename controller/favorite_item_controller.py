from typing import List, Optional

from fastapi import HTTPException, APIRouter

from model.favorite_item import FavoriteItem
from model.favorite_item_request import FavoriteItemRequest
from model.favorite_item_response import FavoriteItemResponse
from repository import favorite_item_repository
from service import favorite_item_service, user_service

router = APIRouter(
    prefix="/favorite_item",
    tags=["favorite_item"]
)


@router.get("/{favorite_item_id}", response_model=Optional[FavoriteItem])
async def get_by_id(favorite_item_id: int) -> Optional[FavoriteItem]:
    favorite_item = await favorite_item_service.get_by_id(favorite_item_id)
    if not favorite_item:
        raise HTTPException(status_code=404, detail=f"favorite item with id:{favorite_item_id} not found...")
    return favorite_item


@router.get("/user/{user_id}", response_model=List[FavoriteItemResponse])
async def get_favorite_items_by_user_id(user_id: int) -> List[FavoriteItemResponse]:
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User with id:{user_id} not found...")
    return await favorite_item_service.get_favorite_items_by_user_id(user_id)


@router.get("/")
async def get_all_favorite_items() -> List[FavoriteItem]:
    return await favorite_item_service.get_all_favorite_items()


@router.post("/")
async def create_favorite_items(favorite_item_request: FavoriteItemRequest):
    try:
        return await favorite_item_service.create_favorite_item(favorite_item_request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{favorite_item_id}", response_model=Optional[FavoriteItem])
async def update_favorite_items(favorite_item_id: int, favorite_item: FavoriteItem):
    favorite_item_exists = await favorite_item_service.get_by_id(favorite_item_id)
    if not favorite_item_exists:
        raise HTTPException(status_code=404, detail=f"Can't update favorite item with id:{favorite_item_id}, favorite item not found...")
    await favorite_item_service.update_favorite_items(favorite_item_id, favorite_item)
    return await favorite_item_service.get_by_id(favorite_item_id)


@router.delete("/{favorite_item_id}")
async def delete_by_id(favorite_item_id: int):
    favorite_item_exists = await favorite_item_service.get_by_id(favorite_item_id)
    if not favorite_item_exists:
        raise HTTPException(status_code=404, detail=f"Can't delete favorite item with id:{favorite_item_id}, favorite item not found...")
    await favorite_item_service.delete_by_id(favorite_item_id)


@router.delete("/{user_id}/item/{item_id}")
async def delete_by_user_and_item_id(user_id: int, item_id: int):
    favorite_item_exists = await favorite_item_repository.get_favorite_item_by_user_and_item(user_id, item_id)
    if not favorite_item_exists:
        raise HTTPException(status_code=404, detail=f"Can't delete favorite item for the user. favorite item not found...")
    await favorite_item_service.delete_by_user_and_item_id(user_id, item_id)

