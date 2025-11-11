from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from .schemas import URLItem, URLResponse
from .services import URLShortenerService
from .database import get_redis, get_cassandra_session


def get_shortener_service(
    redis_client=Depends(get_redis), session=Depends(get_cassandra_session)
) -> URLShortenerService:
    return URLShortenerService(redis_client=redis_client, cassandra_session=session)


# --- Definição das Rotas ---

router = APIRouter()


@router.post("/shorten", response_model=URLResponse)
def create_short_url_endpoint(
    url: URLItem,
    request: Request,
    service: URLShortenerService = Depends(get_shortener_service),
):
    """Endpoint para criar (encurtar) uma nova URL."""

    short_id = service.create_short_url(str(url.long_url))

    base_url = str(request.base_url)
    return URLResponse(short_url=f"{base_url}{short_id}")


@router.get("/{short_id}")
async def redirect_to_long_url_endpoint(
    short_id: str,
    service: URLShortenerService = Depends(get_shortener_service),
):
    """Endpoint de redirecionamento (leitura crítica)."""

    long_url = service.get_long_url(short_id)

    if long_url:
        # Conforme o vídeo, 302 (temporário) para permitir métricas e expiração de cache
        return RedirectResponse(url=long_url, status_code=302)

    # Se o serviço retornar None, a URL não existe
    raise HTTPException(status_code=404, detail="URL não encontrada")
