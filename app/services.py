from hashids import Hashids
from cassandra.query import SimpleStatement
from .config import settings


class URLShortenerService:
    """
    Esta classe encapsula a lógica de negócio principal.
    Ela não sabe nada sobre FastAPI, HTTP, Request ou Response.
    """

    def __init__(self, redis_client, cassandra_session):
        self.redis = redis_client
        self.session = cassandra_session
        self.hashids = Hashids(
            salt=settings.hashids_salt, min_length=settings.hashids_min_length
        )

    def create_short_url(self, long_url: str) -> str:
        """
        Cria, salva e armazena em cache uma nova URL curta.
        Retorna: o 'short_id' gerado.
        """
        # 1. Gerar ID único atômico com Redis
        new_id = self.redis.incr("url:id:counter")

        # 2. Codificar ID para uma string curta
        short_id = self.hashids.encode(new_id)

        # 3. Salvar no Cassandra (fonte da verdade)
        query = SimpleStatement("INSERT INTO urls (short_id, long_url) VALUES (%s, %s)")
        self.session.execute(query, (short_id, long_url))

        # 4. "Aquecer" o cache no Redis para leituras rápidas
        self.redis.set(f"url:{short_id}", long_url, ex=3600)  # Expira em 1h

        return short_id

    def get_long_url(self, short_id: str) -> str | None:
        """
        Busca uma URL longa usando o padrão Cache-Aside.
        Retorna: a 'long_url' ou None se não for encontrada.
        """
        # 1. Tentar ler do Cache (Redis)
        long_url = self.redis.get(f"url:{short_id}")

        if long_url:
            print(f"Cache HIT para: {short_id}")
            return long_url

        # 2. Cache Miss! Buscar no Banco de Dados (Cassandra)
        print(f"Cache MISS para: {short_id}")
        query = SimpleStatement("SELECT long_url FROM urls WHERE short_id = %s")
        row = self.session.execute(query, (short_id,)).one()

        if row:
            long_url = row.long_url

            # 2a. Encontramos no DB -> Salvar no cache para a próxima vez
            self.redis.set(f"url:{short_id}", long_url, ex=3600)

            return long_url

        # 3. Não encontrado em lugar nenhum
        return None
