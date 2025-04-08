from pydantic_settings import BaseSettings


class Config(BaseSettings):
    # POSTGRES
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PORT: int

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Config()
