import hashlib
from cassandra.query import SimpleStatement

# Caracteres para a codificação em Base62
BASE62_CHARS = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def _base62_encode(num: int) -> str:
    """Codifica um número inteiro para uma string em Base62."""
    if num == 0:
        return BASE62_CHARS[0]

    encoded = ""
    while num > 0:
        num, rem = divmod(num, 62)
        encoded = BASE62_CHARS[rem] + encoded
    return encoded


class URLShortenerService:
    """
    Encapsula a lógica de negócio usando hash e Base62.
    """

    def __init__(self, redis_client, cassandra_session):
        self.redis = redis_client
        self.session = cassandra_session
        self.insert_stmt = self.session.prepare(
            "INSERT INTO urls (short_id, long_url) VALUES (?, ?)"
        )
        self.select_stmt = self.session.prepare(
            "SELECT long_url FROM urls WHERE short_id = ?"
        )

    def _get_short_id_for_url(self, long_url: str) -> str:
        """Gera um short_id determinístico usando SHA-256 e Base62."""
        # 1. Criar um hash para a URL
        hasher = hashlib.sha256(long_url.encode("utf-8"))
        # 2. Converter os primeiros 8 bytes do hash para um inteiro
        num = int.from_bytes(hasher.digest()[:8], "big")
        # 3. Codificar em Base62 e pegar os primeiros 7 caracteres
        return _base62_encode(num)[:7]

    def create_short_url(self, long_url: str) -> str:
        """
        Cria ou obtém uma URL curta de forma determinística.
        Retorna: o 'short_id' correspondente.
        """
        short_id = self._get_short_id_for_url(long_url)

        # 1. Verifica se o short_id já existe (colisão ou URL repetida)
        existing_url = self.get_long_url(short_id)

        if existing_url:
            # Se a URL longa for a mesma, encontramos o código existente
            if existing_url == long_url:
                print(f"URL já existe. Retornando short_id: {short_id}")
                return short_id
            # Se a URL for diferente, houve uma colisão de hash.
            print(f"Colisão de Hash detectada para short_id: {short_id}")

        # 2. Salvar no Cassandra
        self.session.execute(self.insert_stmt, (short_id, long_url))

        self.redis.set(f"url:{short_id}", long_url, ex=3600)  # Expira em 1h

        return short_id

    def get_long_url(self, short_id: str) -> str | None:
        """
        Busca uma URL longa usando o padrão Cache-Aside.
        Retorna: a 'long_url' ou None se não for encontrada.
        """
        # 1. Tenta ler do Cache
        cached_url = self.redis.get(f"url:{short_id}")
        if cached_url:
            print(f"Cache HIT para: {short_id}")
            return cached_url

        # 2. Cache Miss! Buscar no Banco de Dados (Cassandra)
        print(f"Cache MISS para: {short_id}")
        row = self.session.execute(self.select_stmt, (short_id,)).one()

        if row:
            long_url = row.long_url
            # Salva no cache
            self.redis.set(f"url:{short_id}", long_url, ex=3600)
            return long_url

        # 3. Não encontrado em lugar nenhum
        return None
