# 🚀 Encurtador de URL com FastAPI, Redis e Cassandra

E aí, tudo bem? 👋
Este é um projetinho de um encurtador de URL. A ideia aqui foi seguir um desafio clássico de _System Design_ (baseado [neste vídeo](https://youtu.be/m_anIoKW7Jg)), mas usando uma stack moderna.
A arquitetura que montamos aqui é ideal para desenvolvimento:

1. **Aplicação (Python):** Roda direto na sua máquina local com o `uv`. Isso te dá _hot-reload_ e facilita o debug.
2. **Serviços (Bancos):** O Redis e o Cassandra rodam isolados dentro do Docker.

## 🔧 O que tem na caixa? (Tech Stack)

- **Aplicação:** Python 3.11 com FastAPI
- **Cache & Gerador de ID:** Redis
- **Banco de Dados Principal:** Cassandra (ótimo para alta escrita, como um encurtador precisa)
- **Orquestração (Bancos):** Docker & Docker Compose
- **Gerenciador de Pacotes:** `uv` (o rapidinho!)

---

## 🏁 Antes de Começar (Pré-requisitos)

Para rodar este projeto, você vai precisar ter algumas coisas instaladas e rodando na sua máquina:

- **Python 3.11:** Isso é **importante**! Nós descobrimos que o driver do Cassandra (`cassandra-driver`) não funciona bem com Python 3.12 ou 3.13 (ele procura um módulo antigo chamado `asyncore`). Usar o 3.11 resolve tudo.
- **Docker Desktop:** Ele precisa estar instalado e **em execução**! É ele quem vai fornecer nosso Redis e Cassandra.
- **`uv`:** O gerenciador de pacotes. Se você não tiver, é só rodar: `pip install uv`
- **Postman** (ou Insomnia, ou `curl`): Alguma ferramenta para a gente testar a API.

---

## 🏃‍♂️ Como Rodar o Projeto (Passo a Passo)

Pronto? Vamos lá!

### 1. Pegue o Código

Se você estiver lendo isso no GitHub, clone o repositório. Se não, só abra a pasta do projeto no seu terminal.

```bash
# Exemplo se fosse clonar:
git clone https://github.com/seu-usuario/seu-repo.git
cd url_shortner_app
```

### 2. Crie o arquivo .env

A nossa aplicação Python (local) precisa saber como "achar" os bancos de dados que estão no Docker.
Crie um arquivo chamado `.env` na raiz do projeto (na mesma pasta do `docker-compose.yml`).
Cole o seguinte conteúdo nele:

```ini
REDIS_HOST=localhost
CASSANDRA_HOST=localhost
```

### 3. Suba os Serviços do Docker

Agora, vamos ligar nossos bancos de dados. Em um terminal, rode:

```bash
docker-compose up -d
```

Isso vai baixar (se for a primeira vez) e iniciar os contêineres do Redis e do Cassandra em segundo plano (`-d`).
Você pode checar se eles estão saudáveis com `docker-compose ps`.

### 4. Crie o Ambiente Virtual (com Python 3.11)

Vamos criar um `.venv` limpo usando o Python 3.11:

```bash
# Deleta o .venv antigo (se existir)
rmdir .venv -Recurse
# Cria o novo .venv usando o Python 3.11
uv venv -p 3.11
```

### 5. Ative o Ambiente

No PowerShell (Windows):

```powershell
.\.venv\Scripts\Activate
```

(Seu terminal agora deve mostrar um `(.venv)` ou `(url_shortner_app)` no início.)

### 6. Instale as Dependências

Agora que estamos no venv, vamos instalar tudo que o `pyproject.toml` pede:

```bash
uv pip install .
```

⚠️ **Aviso!** Se você tiver uma pasta `nginx` sobrando de setups anteriores, esse comando vai falhar. Delete a pasta `nginx` se ela existir! Ela não é usada neste setup.

### 7. Rode a Aplicação!

Tudo pronto! Vamos ligar o servidor FastAPI:

```bash
# Usamos o python -m ... para garantir que ele use o Python 3.11 do venv
python -m uvicorn app.main:app --port 8000 --reload
```

Se tudo deu certo, você verá o Uvicorn iniciar e, logo depois, nossas mensagens de log:

```
Iniciando conexões...
Conectado ao Redis com sucesso!
Conectado ao Cassandra com sucesso!
Iniciando conexões...
Conexões estabelecidas.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

---

## ✅ Como Testar (Usando o Postman)

Com o servidor rodando, vamos criar nossa primeira URL curta!
Abra o Postman.
Configure a requisição assim:

**Método:** `POST`
**URL:** `http://localhost:8000/shorten`

Body > raw > JSON
No corpo (Body), cole o seguinte JSON:

```json
{
  "long_url": "https://pt.wikipedia.org/wiki/Arquitetura_de_software"
}
```

### 📈 Resposta Esperada

Ao clicar em **Send**, você deve receber um `Status: 200 OK` e um JSON de volta:

```json
{
  "short_url": "http://localhost:8000/jR8O2N"
}
```

(O ID `jR8O2N` vai ser diferente para você!)

No seu terminal, você verá o log da aplicação confirmando a requisição:

```
INFO: 127.0.0.1:xxxxx - "POST /shorten HTTP/1.1" 200 OK
Cache MISS para: jR8O2N
```

Prontinho! Agora é só pegar a `short_url` (ex: `http://localhost:8000/jR8O2N`) e colar no seu navegador.
Ele deve te redirecionar para a página da Wikipedia!
