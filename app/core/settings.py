from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    TEST_DATABASE_URL: str

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
