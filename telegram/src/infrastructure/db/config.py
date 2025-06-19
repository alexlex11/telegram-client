from dataclasses import dataclass


@dataclass
class DBConfig:
    host: str = "db"
    port: int = 5432
    database: str = "botdb"
    user: str = "postgres"
    password: str = "postgres"
    echo: bool = True

    @property
    def full_url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"  # noqa
