from fastapi import FastAPI
from contextlib import asynccontextmanager
from .database import (
    connect_to_redis,
    connect_to_cassandra,
    close_redis_connection,
    close_cassandra_connection,
)
from .routes import router as url_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerenciador de 'lifespan' para a aplicação.
    Tudo antes do 'yield' roda na inicialização (startup).
    Tudo depois do 'yield' roda na finalização (shutdown).
    """
    # --- STARTUP ---
    print("Iniciando conexões...")
    connect_to_redis()
    connect_to_cassandra()
    print("Conexões estabelecidas.")

    yield

    # --- SHUTDOWN ---
    print("Fechando conexões...")
    close_redis_connection()
    close_cassandra_connection()
    print("Conexões fechadas.")


app = FastAPI(
    title="Encurtador de URL",
    description="Implementação com FastAPI, Redis e Cassandra (Refatorada com SOLID e UV)",
    lifespan=lifespan,
)

# --- Inclusão das Rotas ---

app.include_router(url_router)


@app.get("/")
def read_root():
    return {"status": "ok", "message": "Serviço de encurtador de URL no ar!"}
