import json
from typing import List

from model.order_item import OrderItem
from repository import cache_repository
from repository.database import database

TABLE_NAME = "order_item"


async def get_order_items_by_order_id(order_id: int) -> List[OrderItem]:
    query = f"""
        SELECT * FROM {TABLE_NAME} WHERE order_id = :order_id
    """
    results = await database.fetch_all(query, values={"order_id": order_id})
    return [OrderItem(**dict(result)) for result in results]


async def get_order_item(order_id: int, item_id: int) -> List[OrderItem]:
    query = f"""
        SELECT * FROM {TABLE_NAME} WHERE order_id = :order_id AND item_id = :item_id
    """
    result = await database.fetch_one(query, values={"order_id": order_id, "item_id": item_id})
    return result


async def get_all_order_items() -> List[OrderItem]:
    query = f"""
        SELECT * FROM {TABLE_NAME}
    """
    results = await database.fetch_all(query)
    return [OrderItem(**dict(result)) for result in results]


async def create_order_items(order_item: OrderItem) -> None:
    query = f"""
        INSERT INTO {TABLE_NAME} (order_id, item_id, quantity)
        VALUES (:order_id, :item_id, :quantity)
    """
    values = {
        "order_id": order_item.order_id,
        "item_id": order_item.item_id,
        "quantity": order_item.quantity
    }
    await database.execute(query, values)


async def update_order_item(order_id: int, order_item: OrderItem) -> None:
    query = f"""
        UPDATE {TABLE_NAME}
        SET quantity = :quantity
        WHERE order_id = :order_id AND item_id = :item_id
    """
    values = {"order_id": order_id, "item_id": order_item.item_id, "quantity": order_item.quantity}
    await database.execute(query, values)

    cache_key = f"temp_order_user_{order_item.order_id}"
    cached_order = cache_repository.get_cache_entity(cache_key)
    if cached_order:
        order_data = json.loads(cached_order)
        for item in order_data["item"]:
            if item["item_id"] == order_item.item_id:
                item["quantity"] = order_item.quantity
        cache_repository.update_cache_entity(cache_key, order_data.json())


async def update_order_item_quantity(order_id: int, item_id: int, quantity: int) -> None:
    query = f"""
        UPDATE {TABLE_NAME}
        SET quantity = :quantity
        WHERE order_id = :order_id AND item_id = :item_id
    """
    values = {"order_id": order_id, "item_id": item_id, "quantity": quantity}
    await database.execute(query, values)


async def delete_all_order_items(order_id: int):
    query = f"""
        DELETE FROM {TABLE_NAME} WHERE order_id = :order_id
    """
    await database.execute(query, values={"order_id": order_id})


async def delete_order_item(order_id: int, item_id: int):
    query = f"""
        DELETE FROM {TABLE_NAME} WHERE order_id = :order_id AND item_id = :item_id
    """
    values = {"order_id": order_id, "item_id": item_id}
    await database.execute(query, values)

    cache_key = f"temp_order_user_{order_id}"
    cached_order = cache_repository.get_cache_entity(cache_key)
    if cached_order:
        order_data = json.loads(cached_order)
        order_data["item"] = [item for item in order_data["item"] if item["item_id"] != item_id]
        cache_repository.update_cache_entity(cache_key, json.dumps(order_data))
