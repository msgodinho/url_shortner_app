import time
import redis

from cassandra.cluster import Cluster, Session
from cassandra.policies import RoundRobinPolicy
from cassandra.connection import ConnectionException
from .config import settings


class DBConnections:
    """Um objeto 'singleton' para armazenar as conexões ativas."""

    redis_client: redis.Redis | None = None
    # 👇 MUDANÇA 2: Corrigir o type-hint aqui
    cassandra_session: Session | None = None
    cassandra_cluster: Cluster | None = None


# Instância única que será importada
connections = DBConnections()


def connect_to_redis():
    """Tenta se conectar ao Redis em loop até ter sucesso."""
    while True:
        try:
            client = redis.Redis(
                host=settings.redis_host, port=6379, db=0, decode_responses=True
            )
            client.ping()
            connections.redis_client = client
            print("Conectado ao Redis com sucesso!")
            break
        except redis.exceptions.ConnectionError as e:
            print(f"Aguardando conexão com o Redis... {e}")
            time.sleep(3)


def connect_to_cassandra():
    """Tenta se conectar ao Cassandra e inicializa o keyspace/tabela."""
    session = None
    cluster = None
    while session is None:
        try:
            cluster = Cluster(
                [settings.cassandra_host], load_balancing_policy=RoundRobinPolicy()
            )
            session = cluster.connect()
        except ConnectionException as e:
            print(f"Aguardando conexão com o Cassandra... {e}")
            time.sleep(5)

    connections.cassandra_session = session
    connections.cassandra_cluster = cluster
    print("Conectado ao Cassandra com sucesso!")

    # Garante que o Keyspace e a Tabela existam
    session.execute(f"""
    CREATE KEYSPACE IF NOT EXISTS {settings.keyspace}
    WITH replication = {{ 'class': 'SimpleStrategy', 'replication_factor': '1' }}
    """)

    session.set_keyspace(settings.keyspace)

    session.execute("""
    CREATE TABLE IF NOT EXISTS urls (
        short_id text PRIMARY KEY,
        long_url text
    )
    """)
    print(f"Keyspace '{settings.keyspace}' e tabela 'urls' prontos.")


def close_redis_connection():
    if connections.redis_client:
        connections.redis_client.close()
        print("Conexão com Redis fechada.")


def close_cassandra_connection():
    if connections.cassandra_session:
        connections.cassandra_session.shutdown()
    if connections.cassandra_cluster:
        connections.cassandra_cluster.shutdown()
    print("Conexão com Cassandra fechada.")


# --- Funções "Getter" para Injeção de Dependência ---


def get_redis() -> redis.Redis:
    """Retorna o cliente Redis. Usado para injeção de dependência."""
    if not connections.redis_client:
        raise RuntimeError("Conexão com Redis não foi inicializada.")
    return connections.redis_client


# 👇 MUDANÇA 3: Corrigir o type-hint de retorno aqui
def get_cassandra_session() -> Session:
    """Retorna a sessão do Cassandra. Usado para injeção de dependência."""
    if not connections.cassandra_session:
        raise RuntimeError("Sessão do Cassandra não foi inicializada.")
    return connections.cassandra_session
