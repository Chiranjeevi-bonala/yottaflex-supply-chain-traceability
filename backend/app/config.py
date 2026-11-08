import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./supply_chain.db")
    debug: bool = True
    secret_key: str = "yottaflex_supply_chain_secret_key_20261022"
    data_seed: int = 20261022
    data_scale: str = "full"

settings = Settings()
