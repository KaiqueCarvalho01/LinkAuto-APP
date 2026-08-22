# 🐳 Guia de Infraestrutura & Docker — LinkAuto

Bem-vindo ao guia de infraestrutura do **LinkAuto**! Este documento foi elaborado tanto para desenvolvedores experientes quanto para contribuidores não-técnicos que desejam rodar, testar e interagir com a aplicação de forma rápida e padronizada.

---

## 📑 Sumário

1. [Visão Geral](#1-visão-geral)
2. [Pré-requisitos](#2-pré-requisitos)
3. [Início Rápido (Em 1 Comando)](#3-início-rápido-em-1-comando)
4. [Tabela de Comandos Essenciais](#4-tabela-de-comandos-essenciais)
5. [Executando Testes via Docker](#5-executando-testes-via-docker)
6. [Banco de Dados & Perfis Opcionais (PostgreSQL + PostGIS)](#6-banco-de-dados--perfis-opcionais)
7. [Guia Passo a Passo para Não-Técnicos (Docker Desktop)](#7-guia-para-não-técnicos)
8. [Troubleshooting & Problemas Frequentes](#8-troubleshooting--problemas-frequentes)

---

## 1. Visão Geral

O LinkAuto utiliza containers Docker para garantir que todos os serviços (Frontend, Backend e Banco de Dados) rodem exatamente com as mesmas dependências e versões em qualquer sistema operacional (Linux, macOS, Windows/WSL2).

### 🏗️ Arquitetura de Containers em Desenvolvimento

```
┌─────────────────────────────────────────────────────────────┐
│                       DOCKER COMPOSE                        │
│                                                             │
│  ┌──────────────────────┐        ┌──────────────────────┐  │
│  │   linkauto-frontend  │        │   linkauto-backend   │  │
│  │     (Node.js 20)     │ ─────> │    (Python 3.11)     │  │
│  │  http://localhost:5173│        │ http://localhost:8000│  │
│  └──────────────────────┘        └──────────┬───────────┘  │
│                                             │               │
│                                  ┌──────────▼───────────┐  │
│                                  │   SQLite Auto-Seed   │  │
│                                  │  (ou PostgreSQL+GIS) │  │
│                                  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

- **Backend (`linkauto-backend`)**: FastAPI, hot-reload ativado, escuta na porta `8000`.
- **Frontend (`linkauto-frontend`)**: React 19 + Vite, HMR (Hot Module Replacement) ativado, escuta na porta `5173`.
- **Banco de Dados (Dev)**: SQLite integrado com seed automático no startup (Admin, Aluno e Instrutores credenciados).

---

## 2. Pré-requisitos

Você precisa apenas do **Docker** e do **Docker Compose** instalados:
- **Windows / macOS**: Instale o [Docker Desktop](https://www.docker.com/products/docker-desktop/).
- **Linux**: Instale o `docker` e o plugin `docker-compose-plugin` (ou `docker compose`).

---

## 3. Início Rápido (Em 1 Comando)

Na raiz do projeto (`LinkAuto-APP`), execute:

```bash
docker compose -f infra/docker-compose.yml up -d
```

Pronto! Os serviços estarão disponíveis em:
- 🌐 **Frontend (Aplicação Web)**: [http://localhost:5173](http://localhost:5173)
- 🔌 **Backend API (Documentação Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- 🩺 **Healthcheck da API**: [http://localhost:8000/health](http://localhost:8000/health)

---

## 4. Tabela de Comandos Essenciais

Todos os comandos devem ser executados a partir da raiz do repositório:

| Ação Desejada | Comando Docker | Descrição |
| :--- | :--- | :--- |
| **Subir serviços em segundo plano** | `docker compose -f infra/docker-compose.yml up -d` | Inicia o backend e o frontend sem travar o terminal. |
| **Subir com reconstrução de imagens** | `docker compose -f infra/docker-compose.yml up -d --build` | Use sempre que novas dependências forem adicionadas ao `package.json` ou `pyproject.toml`. |
| **Ver logs de todos os serviços** | `docker compose -f infra/docker-compose.yml logs -f` | Acompanha os logs em tempo real (Ctrl+C para sair). |
| **Ver logs apenas do Backend** | `docker compose -f infra/docker-compose.yml logs -f backend` | Filtra logs de requisições, erros e seeds da API. |
| **Ver logs apenas do Frontend** | `docker compose -f infra/docker-compose.yml logs -f frontend` | Filtra logs de compilação e HMR do Vite. |
| **Parar todos os serviços** | `docker compose -f infra/docker-compose.yml down` | Encerra os containers com segurança. |
| **Reiniciar todos os serviços** | `docker compose -f infra/docker-compose.yml restart` | Reinicia os containers sem recriar volumes. |
| **Resetar estado e limpar volumes** | `docker compose -f infra/docker-compose.yml down -v` | Remove os volumes anônimos e recria o ambiente limpo. |
| **Ver status dos containers** | `docker compose -f infra/docker-compose.yml ps` | Lista status de saúde (`healthy`), portas e IDs. |

---

## 5. Executando Testes via Docker

Você não precisa ter Python ou Node.js instalados na sua máquina física para rodar as suítes de testes:

### Testes do Backend (Pytest)
```bash
docker compose -f infra/docker-compose.yml exec backend pytest
```

### Testes do Frontend (Vitest)
```bash
docker compose -f infra/docker-compose.yml exec frontend npm test
```

### Checagem de Tipos TypeScript (Frontend)
```bash
docker compose -f infra/docker-compose.yml exec frontend npm run typecheck
```

---

## 6. Banco de Dados & Perfis Opcionais

Por padrão, o ambiente de desenvolvimento utiliza o **SQLite** com reinicialização determinística e seed rico de teste (`RESET_SQLITE_ON_STARTUP=true`).

### 🐘 Ativando o PostgreSQL + PostGIS (Produção/Staging)

Caso queira testar a aplicação integrada com o banco relacional geoespacial PostgreSQL:

```bash
docker compose -f infra/docker-compose.yml --profile postgres up -d
```

Isso inicializará o container `linkauto-postgres` na porta `5432` com a extensão PostGIS habilitada e volume persistente nomeado (`postgres_data`).

---

## 7. Guia Passo a Passo para Não-Técnicos

Se você não tem familiaridade com o terminal:

1. **Abra o Docker Desktop** na sua máquina e certifique-se de que ele está rodando (ícone da baleia verde).
2. **Abra o Terminal** (ou PowerShell no Windows) e navegue até a pasta do projeto.
3. **Cole o comando de inicialização:**
   ```bash
   docker compose -f infra/docker-compose.yml up -d
   ```
4. **No Docker Desktop:**
   - Você verá o grupo de containers `infra` com os serviços `linkauto-backend` e `linkauto-frontend`.
   - Você pode clicar nos botões de Play/Stop ou clicar no serviço para ver os logs graficamente.
5. **No Navegador:**
   - Acesse [http://localhost:5173](http://localhost:5173) para testar a interface do aluno e do instrutor.
   - Acesse [http://localhost:8000/docs](http://localhost:8000/docs) para ver a lista interativa de APIs.

---

## 8. Troubleshooting & Problemas Frequentes

### ❓ Erro: "Port 8000 (ou 5173) is already allocated"
**Causa:** Outro processo local ou container já está usando a porta.  
**Solução:**
```bash
# No Linux/macOS:
lsof -i :8000
lsof -i :5173
# Pare o processo conflitante ou finalize outros containers Docker:
docker stop $(docker ps -q)
```

### ❓ Erro de dependência desatualizada após um `git pull`
**Solução:** Reconstrua as imagens para atualizar pacotes do Node e Python:
```bash
docker compose -f infra/docker-compose.yml up -d --build
```

### ❓ Como resetar o banco de dados de desenvolvimento?
Como o SQLite do backend reseta automaticamente a cada inicialização em ambiente dev (`RESET_SQLITE_ON_STARTUP=true`), basta reiniciar o backend:
```bash
docker compose -f infra/docker-compose.yml restart backend
```
