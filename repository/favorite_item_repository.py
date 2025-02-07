from typing import Optional, List

from model.favorite_item import FavoriteItem
from repository.database import database

TABLE_NAME = "favorite_items"


async def get_by_id(favorite_item_id: int) -> Optional[FavoriteItem]:
    query = f"SELECT * FROM {TABLE_NAME} WHERE id=:favorite_item_id"
    result = await database.fetch_one(query, values={"favorite_item_id": favorite_item_id})
    if result:
        return FavoriteItem(**result)
    else:
        return None


async def get_favorite_items_by_user_id(user_id: int) -> List[FavoriteItem]:
    query = f"SELECT * FROM {TABLE_NAME} WHERE user_id=:user_id"
    results = await database.fetch_all(query, values={"user_id": user_id})
    return [FavoriteItem(**result) for result in results]


async def get_favorite_item_by_user_and_item(user_id: int, item_id: int) -> Optional[FavoriteItem]:
    query = f"""
        SELECT * FROM {TABLE_NAME}
        WHERE user_id = :user_id AND item_id = :item_id
    """
    result = await database.fetch_one(query, values={"user_id": user_id, "item_id": item_id})
    return result


async def get_all_favorite_items() -> List[FavoriteItem]:
    query = f"SELECT * FROM {TABLE_NAME}"
    results = await database.fetch_all(query)
    return [FavoriteItem(**result) for result in results]


async def create_favorite_item(favorite_item: FavoriteItem) -> Optional[int]:
    query = f"""
        INSERT INTO {TABLE_NAME} (user_id, item_id)
        VALUES (:user_id, :item_id)
    """
    values = {
        "user_id": favorite_item.user_id,
        "item_id": favorite_item.item_id,
    }
    async with database.transaction():
        await database.execute(query, values)
        last_record_id = await database.fetch_one("SELECT LAST_INSERT_ID()")
    return last_record_id[0] if last_record_id else None


async def update_favorite_items(favorite_item_id: int, favorite_item: FavoriteItem):
    query = f"""
        UPDATE {TABLE_NAME} 
        SET user_id = :user_id,
            item_id = :item_id
        WHERE id = :favorite_item_id
    """
    values = {
        "favorite_item_id": favorite_item_id,
        "user_id": favorite_item.user_id,
        "item_id": favorite_item.item_id,
    }
    await database.execute(query, values)


async def delete_by_id(favorite_item_id: int):
    query = f"DELETE FROM {TABLE_NAME} WHERE id=:favorite_item_id"
    await database.execute(query, values={"favorite_item_id": favorite_item_id})


async def delete_by_user_and_item_id(user_id: int, item_id: int):
    query = f"DELETE FROM {TABLE_NAME} WHERE user_id=:user_id AND item_id=:item_id"
    await database.execute(query, values={"user_id": user_id, "item_id": item_id})


async def delete_favorites_by_user_id(user_id: int):
    query = f"DELETE FROM {TABLE_NAME} WHERE user_id = :user_id"
    await database.execute(query, values={"user_id": user_id})


async def delete_favorite_items_by_item_id(item_id: int):
    query = f"DELETE FROM {TABLE_NAME} WHERE item_id=:item_id"
    await database.execute(query, values={"item_id": item_id})


