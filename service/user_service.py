from typing import Optional, List

from passlib.context import CryptContext

from exceptions.security_exceptions import username_taken_exception
from model.user import User
from model.user_request import UserRequest
from model.user_response import UserResponse
from repository import user_repository, favorite_item_repository, order_repository
from service import order_service

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str):
    return bcrypt_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return bcrypt_context.verify(plain_password, hashed_password)


async def validate_unique_username(username: str) -> bool:
    user_exists = await user_repository.get_user_by_username(username)
    return user_exists is None


def user_to_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        address=user.address,
        country=user.country,
        city=user.city,
    )


async def get_user_by_id(user_id: int) -> Optional[UserResponse]:
    user = await user_repository.get_user_by_id(user_id)
    return user_to_response(user) if user else None


async def get_user_by_username(username: str) -> Optional[User]:
    user = await user_repository.get_user_by_username(username)
    return user


async def get_all_users() -> List[UserResponse]:
    users = await user_repository.get_all_users()
    return [user_to_response(user) for user in users]


async def create_user(user_request: UserRequest):
    if await validate_unique_username(user_request.username):
        hashed_password = get_password_hash(user_request.password)
        await user_repository.create_user(user_request, hashed_password)
    else:
        raise username_taken_exception()


async def update_user_by_id(user_id: int, user_request: UserRequest):
    hashed_password = get_password_hash(user_request.password) if user_request.password else None
    await user_repository.update_user_by_id(user_id, user_request, hashed_password)


async def login_user(user_id: int):
    await user_repository.login_user(user_id)


async def logout_user(user_id: int):
    await user_repository.logout_user(user_id)


async def delete_user_by_id(user_id):
    user_orders = await order_service.get_order_by_user_id(user_id)
    user_favorites = await favorite_item_repository.get_favorite_items_by_user_id(user_id)
    if user_orders:
        await order_repository.delete_order_by_user_id(user_id)
    if user_favorites:
        await favorite_item_repository.delete_favorites_by_user_id(user_id)
    await user_repository.delete_user_by_id(user_id)


