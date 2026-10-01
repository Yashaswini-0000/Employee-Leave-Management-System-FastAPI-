from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    mysql_database_url: str
    secret_key: str
    access_token_expire_minutes: int = 30
    algorithm: str = "HS256"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
