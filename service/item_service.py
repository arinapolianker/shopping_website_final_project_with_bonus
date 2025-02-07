from typing import Optional, List

from model.item import Item
from repository import item_repository, favorite_item_repository, order_repository, order_item_repository


async def get_item_by_id(item_id: int) -> Optional[Item]:
    return await item_repository.get_item_by_id(item_id)


async def get_item_by_name(item_name: str):
    return await item_repository.get_item_by_name(item_name)


async def get_all_items() -> List[Item]:
    return await item_repository.get_all_items()


async def create_item(item: Item) -> int:
    return await item_repository.create_item(item)


async def update_item(item_id: int, item: Item):
    await item_repository.update_item(item_id, item)


async def delete_item_by_id(item_id: int):
    favorite_items = await favorite_item_repository.get_all_favorite_items()
    favorite_item_ids = {item.item_id for item in favorite_items}
    if item_id in favorite_item_ids:
        await favorite_item_repository.delete_favorite_items_by_item_id(item_id)

    temp_orders = await order_repository.get_all_temp_orders()
    for order in temp_orders:
        order_items = await order_item_repository.get_order_items_by_order_id(order.id)
        order_item_ids = {order_item.item_id for order_item in order_items}
        if item_id in order_item_ids:
            await order_item_repository.delete_order_item(order.id, item_id)
    await item_repository.delete_item_by_id(item_id)
