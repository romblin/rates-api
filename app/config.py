from pydantic import BaseSettings


class Settings(BaseSettings):
    DATABASE: str = 'rates'
    DATABASE_HOST: str = 'localhost'
    DATABASE_PORT: int = 27017


settings = Settings()
