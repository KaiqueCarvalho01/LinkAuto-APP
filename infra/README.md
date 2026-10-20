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
7. [Guia Passo a Passo para Não-Técnicos (Docker Desktop)](#7-guia-passo-a-passo-para-não-técnicos)
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
│  │     (Node.js 22)     │ ─────> │    (Python 3.14)     │  │
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
| **Subir com reconstrução de imagens** | `docker compose -f infra/docker-compose.yml up -d --build -V` | Use sempre que novas dependências forem adicionadas ao `package.json` ou `pyproject.toml`. O `-V` (`--renew-anon-volumes`) recria os volumes de `node_modules` e `.venv`; sem ele, os containers continuam com os pacotes antigos. |
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

### 🐘 Ativando o PostgreSQL + PostGIS

Caso queira testar a aplicação integrada com o banco relacional geoespacial PostgreSQL (ainda como ambiente de desenvolvimento, `APP_ENV=development`, com o `JWT_SECRET` de exemplo):

```bash
docker compose -f infra/docker-compose.yml --profile postgres up -d
```

Além dos serviços padrão, o perfil `postgres` sobe:

| Serviço | Porta | Função |
| :--- | :--- | :--- |
| `postgres` | `5432` | PostgreSQL 16 + PostGIS com volume persistente (`postgres_data`). |
| `migrate` | — | Passo de *release*: roda `scripts/migrate.sh` (`alembic upgrade head`) e encerra. |
| `backend-postgres` | `8001` | Backend apontando para o Postgres; só inicia depois que `migrate` termina com sucesso. |

Para aplicar novas migrações sem reiniciar tudo:

```bash
docker compose -f infra/docker-compose.yml --profile postgres run --rm migrate
```

### 🚀 Migrações no Deploy (Produção)

O servidor **nunca** altera o schema sozinho: `uvicorn` não roda migrações no startup e o `create_all` só é usado no SQLite de desenvolvimento. Em todo deploy que traga uma nova revisão do Alembic, rode o passo de release **uma única vez**, **antes** de a nova versão receber tráfego:

```bash
# Mesma imagem de produção e mesmas variáveis de ambiente da aplicação
docker run --rm --env-file prod.env linkauto-backend:<tag> scripts/migrate.sh
```

- **CI/CD:** um job de pré-deploy que executa o comando acima e bloqueia o rollout se falhar.
- **Kubernetes:** um `Job` (ex.: hook `pre-upgrade` do Helm) ou um *init container* em um Deployment de **uma** réplica.
- **Não** rode as migrações no startup de cada réplica: várias réplicas subindo ao mesmo tempo disputam o mesmo schema.
- Escreva migrações compatíveis com a versão anterior (*expand/contract*), já que a versão antiga continua servindo enquanto a nova sobe.

### 🌐 Imagem de Produção do Frontend

O frontend é um SPA estático servido por Nginx sem privilégios (porta `8080`). A URL pública da API entra no bundle em tempo de build e é **obrigatória** (o build falha sem ela):

```bash
docker build --target production \
  --build-arg VITE_API_BASE_URL=https://api.seu-dominio.com.br/api/v1 \
  -t linkauto-frontend:<tag> linkauto-frontend
docker run -d -p 80:8080 linkauto-frontend:<tag>
```

- Rotas do app (`/my-lessons`, `/password-reset/confirm?token=...`) caem no `index.html`, então recarregar a página e abrir links de e-mail funciona.
- `/assets/` tem cache longo (arquivos com hash); o `index.html` é sempre revalidado.
- `GET /health` responde `ok` (usado pelo `HEALTHCHECK` da imagem).
- Defina `FRONTEND_URL` do backend com a URL pública deste frontend (links nos e-mails e na redefinição de senha).

### ⏰ Jobs Agendados (Agendamentos)

Estes jobs mantêm os agendamentos e os tokens em dia e precisam rodar periodicamente:

| Job | O que faz |
| :--- | :--- |
| `timeout` | Cancela (como `SISTEMA`) solicitações `PENDENTE` criadas há mais de 24h, libera os horários e avisa aluno e instrutor. |
| `completion` | Marca como `REALIZADA` as aulas `CONFIRMADA` que terminaram há 2h ou mais (necessário para as avaliações). |
| `reminder` | Envia o lembrete de 24h (quando o e-mail está configurado) e marca o agendamento como lembrado. |
| `token-cleanup` | Apaga refresh tokens e links de redefinição de senha vencidos há mais de 1 dia (a folga mantém a detecção de reuso de tokens recém-vencidos). |

Eles rodam com a mesma imagem e as mesmas variáveis de ambiente da aplicação, sem HTTP nem token de admin:

```bash
python -m app.jobs run all                 # ou: run timeout completion reminder token-cleanup
docker run --rm --env-file prod.env linkauto-backend:<tag> python -m app.jobs run all
```

- Imprime um resumo JSON por job e termina com código `1` se algum agendamento falhar.
- **Agende uma única vez por ambiente**, a cada **15 minutos**: um `CronJob` do Kubernetes (`schedule: "*/15 * * * *"`, `concurrencyPolicy: Forbid`), o agendador da plataforma ou um cron. **Não** rode em cada réplica da API.
- Rodar duas vezes (inclusive ao mesmo tempo) é seguro: cada agendamento é reservado com um `UPDATE` condicional, então só uma execução cancela, conclui ou envia o lembrete.
- Localmente, o serviço `scheduler` do compose (e `scheduler-postgres`, no perfil `postgres`) roda `run all` a cada `JOBS_INTERVAL_SECONDS` (padrão 900).
- Os endpoints `POST /api/v1/jobs/booking-{timeout,completion,reminder}` continuam disponíveis para execuções manuais por admins.

> [!NOTE]
> Em desenvolvimento o backend SQLite continua usando `create_all` + seed a cada startup. Trocar o fluxo de dev para migrações + seed é uma mudança de workflow que ainda precisa ser acordada com o time (ver issue #28).

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
**Solução:** Reconstrua as imagens e recrie os volumes de dependências (`-V`), senão os volumes anônimos de `node_modules` e `.venv` continuam escondendo os pacotes novos da imagem:
```bash
docker compose -f infra/docker-compose.yml up -d --build -V
```

### ❓ Como resetar o banco de dados de desenvolvimento?
Como o SQLite do backend reseta automaticamente a cada inicialização em ambiente dev (`RESET_SQLITE_ON_STARTUP=true`), basta reiniciar o backend:
```bash
docker compose -f infra/docker-compose.yml restart backend
```
