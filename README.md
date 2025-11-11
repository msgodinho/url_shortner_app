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
- **Gerenciador de Pacotes:** `uv`
- **Load Balancer:** Nginx

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
git clone https://github.com/msgodinho/url_shortner_app.git
cd url_shortner_app
```

### 2. Suba os Serviços do Docker

Agora, vamos ligar todos os serviços (Redis, Cassandra, duas instâncias da aplicação FastAPI e Nginx). Em um terminal, rode:

```bash
docker-compose up -d --build
```

Isso vai construir as imagens da aplicação (se for a primeira vez ou se houver mudanças no código), baixar outras imagens (Redis, Cassandra, Nginx) e iniciar todos os contêineres em segundo plano (`-d`).
Você pode checar se eles estão saudáveis com `docker-compose ps -a`.

### 3. Verifique o status dos serviços

Aguarde alguns instantes para que todos os serviços estejam completamente inicializados e saudáveis. Você pode monitorar o status com:

```bash
docker-compose ps -a
```

E verificar os logs para garantir que a aplicação FastAPI está rodando sem erros:

```bash
docker-compose logs app1
docker-compose logs app2
```

Você deve ver mensagens indicando que as conexões com Redis e Cassandra foram estabelecidas.


---

## ✅ Como Testar (Usando o Postman)

Com o servidor rodando, vamos criar nossa primeira URL curta!
Abra o Postman.
Configure a requisição assim:

**Método:** `POST`
**URL:** `http://localhost/shorten`

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
  "short_url": "http://localhost/jR8O2N"
}
```

(O ID `jR8O2N` vai ser diferente para você!)

No seu terminal, você verá o log da aplicação confirmando a requisição:

```
INFO: 127.0.0.1:xxxxx - "POST /shorten HTTP/1.1" 200 OK
Cache MISS para: jR8O2N
```

Ele deve te redirecionar para a página da Wikipedia!
