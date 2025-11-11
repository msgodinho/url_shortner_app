from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Carrega variáveis de ambiente para a configuração da app."""

    # Padrões 'redis' e 'cassandra' funcionam com os nomes do Docker Compose
    redis_host: str = "redis"
    cassandra_host: str = "cassandra"
    keyspace: str = "url_shortener"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
