from typing import Optional

from pydantic import BaseModel


class User(BaseModel):
    id: Optional[int]
    first_name: str
    last_name: str
    email: str
    phone: str
    address: str
    country: str
    city: str
    username: str
    hashed_password: str
    is_logged: bool
