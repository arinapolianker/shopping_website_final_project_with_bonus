from datetime import date
from typing import List, Optional
import json

from model.order import Order
from model.order_status import OrderStatus
from repository import cache_repository, order_item_repository
from repository.database import database
from service import item_service

TABLE_NAME = "orders"


async def cache_temp_order(order_id: int, order: Order):
    order_items = await order_item_repository.get_order_items_by_order_id(order_id)

    items = []
    total_price = 0
    for order_item in order_items:
        item = await item_service.get_item_by_id(order_item.item_id)
        if not item:
            continue
        items.append({
            "item_id": item.id,
            "name": item.name,
            "price": item.price,
            "quantity": order_item.quantity,
            "item_stock": item.item_stock
        })
        total_price += item.price * order_item.quantity

    cache_key = f"temp_order_user_{order.user_id}"
    order_data = order.dict()
    order_data.update({
        "id": order_id,
        "item": items,
        "total_price": total_price,
        "shipping_address": order.shipping_address,
        "order_date": order.order_date.isoformat(),
        "status": order.status.value
    })

    cache_repository.create_cache_entity(cache_key, json.dumps(order_data))


async def get_order_by_id(order_id: int) -> Optional[Order]:
    query = f"SELECT * FROM {TABLE_NAME} WHERE id=:order_id"
    result = await database.fetch_one(query, values={"order_id": order_id})
    return Order(**result) if result else None


async def get_order_by_user_id(user_id: int) -> List[Order]:
    query = f"SELECT * FROM {TABLE_NAME} WHERE user_id=:user_id"
    results = await database.fetch_all(query, values={"user_id": user_id})
    return [Order(**result) for result in results]


async def get_temp_order_by_user_id(user_id: int) -> Optional[Order]:
    cache_key = f"temp_order_user_{user_id}"
    cached_order = cache_repository.get_cache_entity(cache_key)
    if cached_order:
        temp_order = json.loads(cached_order)
        return Order(**temp_order)

    query = f"""
            SELECT * FROM {TABLE_NAME}
            WHERE user_id = :user_id AND status = 'TEMP'
            ORDER BY order_date DESC LIMIT 1
        """
    result = await database.fetch_one(query, values={"user_id": user_id})
    if result:
        order = Order(**result)
        cache_repository.create_cache_entity(cache_key, order.json())
        return order
    return None


async def get_all_temp_orders() -> List[Order]:
    query = f"SELECT * FROM {TABLE_NAME} WHERE status = 'TEMP'"
    results = await database.fetch_all(query)
    return [Order(**result) for result in results]


async def get_all_orders() -> List[Order]:
    query = f"SELECT * FROM {TABLE_NAME}"
    results = await database.fetch_all(query)
    return [Order(**result) for result in results]


async def create_order(order: Order) -> Optional[int]:
    query = f"""
        INSERT INTO {TABLE_NAME} (user_id, order_date, shipping_address, total_price, status)
        VALUES (:user_id, :order_date, :shipping_address, :total_price, :status)
    """
    values = {
        "user_id": order.user_id,
        "order_date": order.order_date,
        "shipping_address": order.shipping_address,
        "total_price": order.total_price,
        "status": order.status.value
    }

    async with database.transaction():
        await database.execute(query, values)
        last_record_id = await database.fetch_one("SELECT LAST_INSERT_ID()")
        order_id = last_record_id[0] if last_record_id else None

    if order_id and order.status.value == "TEMP":
        await cache_temp_order(order_id, order)

    return order_id


async def update_order(order_id: int, order: Order):
    query = f"""
        UPDATE {TABLE_NAME}
        SET user_id = :user_id, 
        order_date = :order_date, 
        shipping_address = :shipping_address, 
        total_price = :total_price,
        status = :status
        WHERE id = :order_id
    """
    values = {
        "order_id": order_id,
        "user_id": order.user_id,
        "order_date": order.order_date,
        "shipping_address": order.shipping_address,
        "total_price": order.total_price,
        "status": order.status.value
    }
    await database.execute(query, values)


async def update_temp_order(order_id: int, total_price: float):
    query = f"""
        UPDATE {TABLE_NAME}
        SET total_price = :total_price
        WHERE id = :order_id AND status = 'TEMP'
    """
    values = {
        "total_price": total_price,
        "order_id": order_id
    }
    await database.execute(query, values)
    order = await get_order_by_id(order_id)
    cache_key = f"temp_order_user_{order.user_id}"
    if order and order.status.value == "TEMP":
        cache_repository.update_cache_entity(cache_key, order.json())


async def update_order_status(order_id: int, shipping_address: str, status: OrderStatus, date_close: date):
    order = await get_order_by_id(order_id)
    query = f"""
        UPDATE {TABLE_NAME}
        SET order_date = :order_date, shipping_address = :shipping_address, status = :status
        WHERE id = :order_id
    """
    values = {
        "order_id": order_id,
        "order_date": date_close.isoformat(),
        "shipping_address": shipping_address,
        "status": status.value
    }
    await database.execute(query, values)
    cache_key = f"temp_order_user_{order.user_id}"
    cache_repository.remove_cache_entity(cache_key)


async def delete_order_by_id(order_id: int):
    order = await get_order_by_id(order_id)
    query = f"DELETE FROM {TABLE_NAME} WHERE id=:order_id"
    await database.execute(query, values={"order_id": order_id})
    cache_key = f"temp_order_user_{order.user_id}"
    cache_repository.remove_cache_entity(cache_key)


async def delete_order_by_user_id(user_id: int):
    query = f"DELETE FROM {TABLE_NAME} WHERE user_id=:user_id"
    await database.execute(query, values={"user_id": user_id})
