from pydantic import BaseModel, HttpUrl


class URLItem(BaseModel):
    """Schema para a entrada (POST /shorten)"""

    # Usar HttpUrl já valida se a string é uma URL válida
    long_url: HttpUrl


class URLResponse(BaseModel):
    """Schema para a saída (POST /shorten)"""

    short_url: str
