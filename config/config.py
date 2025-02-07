from pydantic import BaseSettings


class Config(BaseSettings):
    MYSQL_USER: str = "user"
    MYSQL_PASSWORD: str = "password"
    MYSQL_DATABASE: str = "main"
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: str = "3306"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: str = "6379"
    REDIS_TTL: int = 100
    DATABASE_URL: str = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    SECRET_KEY: str = "secret_key_app"
    ALGORITHM: str = "HS256"
    TOKEN_EXPIRY_TIME: float = 20.0
