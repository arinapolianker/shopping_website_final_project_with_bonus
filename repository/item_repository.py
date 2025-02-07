import json
from typing import Optional, List

from model.item import Item
from repository import cache_repository
from repository.database import database


TABLE_NAME = "item"


async def get_item_by_id(item_id: int) -> Optional[Item]:
    cache_key = f"item_id_{item_id}"
    cached_item = cache_repository.get_cache_entity(cache_key)
    if cached_item:
        item_data = json.loads(cached_item)
        return Item(**item_data)

    query = f"SELECT * FROM {TABLE_NAME} WHERE id=:item_id"
    result = await database.fetch_one(query, values={"item_id": item_id})
    if result:
        item = Item(**result)
        cache_repository.create_cache_entity(cache_key, item.json())
        return item
    else:
        return None


async def get_item_by_name(item_name: str):
    query = f"SELECT * FROM {TABLE_NAME} WHERE name=:item_name"
    result = await database.fetch_one(query, values={"item_name": item_name})
    return Item(**result) if result else None


async def get_all_items() -> List[Item]:
    cache_key = "all_items"
    cached_items = cache_repository.get_cache_entity(cache_key)
    if cached_items:
        return [Item(**item) for item in json.loads(cached_items)]
    query = f"SELECT * FROM {TABLE_NAME}"
    results = await database.fetch_all(query)
    if results:
        items = [Item(**result) for result in results]
        cache_repository.create_cache_entity(
            cache_key, json.dumps([json.loads(item.json()) for item in items])
        )
        return items

    return []


async def create_item(item: Item) -> int:
    query = f"""
        INSERT INTO {TABLE_NAME} (name, price, item_stock)
        VALUES (:name, :price, :item_stock)
    """
    values = {
        "name": item.name,
        "price": item.price,
        "item_stock": item.item_stock
    }
    async with database.transaction():
        await database.execute(query, values)
        last_record_id = await database.fetch_one("SELECT LAST_INSERT_ID()")

    item_cache_data = {
        "id": last_record_id["id"],
        "name": item.name,
        "price": item.price,
        "item_stock": item.item_stock
    }
    cache_repository.create_cache_entity(f"item_id_{last_record_id['id']}", json.dumps(item_cache_data))
    cache_repository.remove_cache_entity("all_items")
    return last_record_id["id"]


async def update_item(item_id: int, item: Item):
    query = f"""
        UPDATE {TABLE_NAME}
        SET name = :name, price = :price, item_stock = :item_stock
        WHERE id = :item_id
    """
    values = {
        "item_id": item_id,
        "name": item.name,
        "price": item.price,
        "item_stock": item.item_stock
    }
    await database.execute(query, values)

    cache_key = f"item_id_{item_id}"
    item_cache_data = item.json()
    cache_repository.update_cache_entity(cache_key, item_cache_data)
    cache_repository.remove_cache_entity("all_items")


async def delete_item_by_id(item_id: int):
    cache_key = f"item_id_{item_id}"
    cache_repository.remove_cache_entity(cache_key)
    cache_repository.remove_cache_entity("all_items")
    query = f"DELETE FROM {TABLE_NAME} WHERE id=:item_id"
    await database.execute(query, values={"item_id": item_id})
