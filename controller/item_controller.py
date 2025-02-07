from typing import List

from fastapi import HTTPException, APIRouter

from model.item import Item
from service import item_service

router = APIRouter(
    prefix="/item",
    tags=["item"]
)


@router.get("/{item_id}", response_model=Item)
async def get_item_by_id(item_id: int):
    item = await item_service.get_item_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Item with id: {item_id} not found")
    return item


@router.get("/", response_model=List[Item])
async def get_all_items():
    return await item_service.get_all_items()


@router.post("/", response_model=Item)
async def create_item(item: Item):
    item_exists = await item_service.get_item_by_name(item.name)
    if item_exists:
        raise HTTPException(status_code=404, detail=f"Can't create item, item: '{item.name}' already exists.")
    item_id = await item_service.create_item(item)
    return await item_service.get_item_by_id(item_id)


@router.put("/{item_id}", response_model=Item)
async def update_item(item_id: int, item: Item):
    item_exist = await item_service.get_item_by_id(item_id)
    if not item_exist:
        raise HTTPException(status_code=404, detail=f"Can't update item with id: {item_id}, item not found")
    await item_service.update_item(item_id, item)
    return await item_service.get_item_by_id(item_id)


@router.delete("/{item_id}")
async def delete_item(item_id: int):
    item_exist = await item_service.get_item_by_id(item_id)
    if not item_exist:
        raise HTTPException(status_code=404, detail=f"Item with id: {item_id} not found")
    await item_service.delete_item_by_id(item_id)

