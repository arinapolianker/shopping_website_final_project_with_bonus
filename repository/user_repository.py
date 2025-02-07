import json
from typing import Optional, List

from model.user import User
from model.user_request import UserRequest
from repository import cache_repository
from repository.database import database

TABLE_NAME = "users"


async def get_user_by_id(user_id: int) -> Optional[User]:
    if cache_repository.is_key_exists(str(user_id)):
        string_user = cache_repository.get_cache_entity(str(user_id))
        user_data = json.loads(string_user)
        if user_data:
            query = f"SELECT * FROM {TABLE_NAME} WHERE id=:user_id"
            result = await database.fetch_one(query, values={"user_id": user_id})
            if result:
                return User(**result)
    else:
        query = f"SELECT * FROM {TABLE_NAME} WHERE id=:user_id"
        result = await database.fetch_one(query, values={"user_id": user_id})
        if result:
            user = User(**result)
            user_cache_data = {
                "id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "is_logged": user.is_logged
            }
            cache_repository.create_cache_entity(str(user_id), json.dumps(user_cache_data))
            return user
        else:
            return None


async def get_user_by_username(username: str) -> Optional[User]:
    query = f"SELECT * FROM {TABLE_NAME} WHERE username=:username"
    result = await database.fetch_one(query, values={"username": username})
    if result:
        return User(**result)
    else:
        return None


async def get_all_users() -> List[User]:
    query = f"SELECT * FROM {TABLE_NAME} WHERE is_logged=:is_logged"
    results = await database.fetch_all(query, values={"is_logged": True})
    return [User(**result) for result in results]


async def create_user(user: UserRequest, hashed_password: str):
    query = f"""
        INSERT INTO {TABLE_NAME} (first_name, last_name, email, phone, address, country, city, username, hashed_password, is_logged)
        VALUES (:first_name, :last_name, :email, :phone, :address, :country, :city, :username, :hashed_password, :is_logged)
    """
    user_dict = user.dict()
    del user_dict["password"]
    values = {**user_dict, "hashed_password": hashed_password, "is_logged": True}
    async with database.transaction():
        await database.execute(query, values)
        last_record_id = await database.fetch_one("SELECT LAST_INSERT_ID()")

    user_id = last_record_id[0]
    user_cache_data = {
        "id": user_id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "is_logged": True
    }
    cache_repository.create_cache_entity(str(user_id), json.dumps(user_cache_data))


async def update_user_by_id(user_id: int, user: UserRequest, hashed_password: Optional[str] = None):
    query = f"""
        UPDATE {TABLE_NAME} 
        SET first_name = :first_name,
        last_name = :last_name,
        email = :email,
        address = :address,
        country = :country,
        city = :city,
        username = :username,
        {"hashed_password = :hashed_password" if hashed_password else ""}
        WHERE id = :user_id
    """
    values = {
        "user_id": user_id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "address": user.address,
        "country": user.country,
        "city": user.city,
        "username": user.username
    }
    if hashed_password:
        values["hashed_password"] = hashed_password

    await database.execute(query, values=values)


async def login_user(user_id: int):
    query = f"""
        UPDATE {TABLE_NAME} 
        SET is_logged = :is_logged
        WHERE id = :user_id
    """
    values = {
        "user_id": user_id,
        "is_logged": True
    }

    await database.execute(query, values=values)


async def logout_user(user_id: int):
    query = f"""
           UPDATE {TABLE_NAME} 
           SET is_logged = :is_logged
           WHERE id = :user_id
       """
    values = {
        "user_id": user_id,
        "is_logged": False
    }

    await database.execute(query, values=values)


async def delete_user_by_id(user_id: int):
    cache_repository.remove_cache_entity(str(user_id))
    query = f"DELETE FROM {TABLE_NAME} WHERE id=:user_id"
    await database.execute(query, values={"user_id": user_id})

    cache_key = f"temp_order_user_{user_id}"
    cache_repository.remove_cache_entity(cache_key)

