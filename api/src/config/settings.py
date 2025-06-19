from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    class Config:
        env_file = "api.env"

    mode: Literal["DEV", "TEST", "PROD"] = Field(..., env="MODE")
    log_level: str = Field(..., env="LOG_LEVEL")

    db_name: str = Field(..., env="DB_NAME")
    db_user: str = Field(..., env="DB_USER")
    db_port: str = Field(..., env="DB_PORT")
    db_host: str = Field(..., env="DB_HOST")
    db_pass: str = Field(..., env="DB_PASS")

    bot_host: str = Field(..., env="BOT_HOST")
    bot_port: str = Field(..., env="BOT_PORT")

    secret: str = Field(..., env="SECRET")
    hash: str = Field(..., env="HASH")

    bot_api_url: str = "http://bots:1111"
    all_teleton_accounts_endpoint: str = "/cmd/bt/info/all"

    ai_api_key: str = "sk-aitunnel-eV4bAJe176l5ARPXtxmjV3rjJV90j4M6"
    ai_base_url: str = "https://api.aitunnel.ru/v1/"

    @property
    def db_url(self):
        return (
            f"postgresql+psycopg2://{self.db_user}:{self.db_pass}@"
            f"{self.db_host}:{self.db_port}/{self.db_name}"
        )


settings = Settings()
