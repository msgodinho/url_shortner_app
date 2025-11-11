FROM python:3.10-slim

WORKDIR /code

# 1. Instala o 'uv'
RUN pip install uv

# 2. Copia o pyproject.toml
COPY ./pyproject.toml /code/pyproject.toml

# 3. Instala as dependências
RUN uv pip install --system --no-cache .

# 4. Copia o código-fonte da aplicação
COPY ./app /code/app

# 5. Expõe a porta e define o comando de execução
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]