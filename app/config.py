from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Carrega variáveis de ambiente para a configuração da app."""

    # Padrões 'redis' e 'cassandra' funcionam com os nomes do Docker Compose
    redis_host: str = "redis"
    cassandra_host: str = "cassandra"
    keyspace: str = "url_shortener"

    class Config:
        # Permite que as variáveis de ambiente (ex: REDIS_HOST) sejam lidas
        env_file = ".env"
        env_file_encoding = "utf-8"


# Instância única das configurações, importada por outros módulos
settings = Settings()
