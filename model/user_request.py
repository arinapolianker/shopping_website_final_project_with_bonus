from pydantic import BaseModel


class UserRequest(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str
    address: str
    country: str
    city: str
    username: str
    password: str
