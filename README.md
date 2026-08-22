![LinkAuto Logo](docs/images/LinkAuto-logo-square.webp)

Plataforma mobile-first para conectar alunos e instrutores autonomos de transito.

Idioma:

- PT-BR: [README.md](README.md)
- US-EN: [docs/README.en.md](docs/README.en.md)

Navegacao rapida:

- [Visao geral](#visao-geral)
- [Status atual](#status-atual)
- [Como executar](#como-executar-localmente)
- [Qualidade e testes](#qualidade-e-testes)
- [Seguranca](docs/SECURITY_TECHNIQUES.md)

![LinkAuto Banner](docs/images/LinkAuto-banner.webp)

> [!IMPORTANT]
> Este README descreve o estado atual do codigo neste repositorio.
> O source-of-truth funcional e contratual da feature V1 esta em specs/001-user-booking-domains.

## Visao geral

O LinkAuto organiza o fluxo de descoberta de instrutores, autenticacao, validacao administrativa e (na proxima fase) agendamento completo com regras de negocio para Booking.

Escopo funcional consolidado da V1:

- Usuario multi-role (ALUNO, INSTRUTOR, ADMIN)
- Fluxo de autenticacao com access token + refresh token via cookie
- Validacao administrativa de instrutor
- Upload de documentos de credenciamento com validacoes de seguranca
- Contrato OpenAPI para slots, booking, mensagens e reviews

Referencias principais:

- [specs/001-user-booking-domains/spec.md](specs/001-user-booking-domains/spec.md)
- [specs/001-user-booking-domains/plan.md](specs/001-user-booking-domains/plan.md)
- [specs/001-user-booking-domains/tasks.md](specs/001-user-booking-domains/tasks.md)
- [specs/001-user-booking-domains/contracts/api-v1-openapi.yaml](specs/001-user-booking-domains/contracts/api-v1-openapi.yaml)
- [docs/SECURITY_TECHNIQUES.md](docs/SECURITY_TECHNIQUES.md)

## Status atual

### Progresso por fase

| Fase | Estado |
| --- | --- |
| Phase 1 - Setup | Concluida |
| Phase 2 - Foundational | Concluida |
| Phase 3 - US1 | Concluida |
| Phase 4 - US2 | Concluída |
| Phase 5 - US3 | Concluída |
| Phase 6 - Polish | Concluída |

### O que ja esta implementado

Backend:

- **Infraestrutura Fundacional (Phase 1-2):** FastAPI versionado (/api/v1), envelopes comuns, banco SQLite, JWT access/refresh e RBAC de alta segurança.
- **US1 (Cadastro, Login & Admin):** Fluxo completo de cadastro, login, uploads de documentos com limites e aprovação/rejeição pelo Admin.
- **US2 (Booking & Slots):** Gerenciamento e listagem de slots de 1h, solicitação de agendamentos consecutivos (mínimo 2 slots), máquina de estados de agendamentos e penalidade automática de 7 dias para cancelamentos a menos de 24h da aula.
- **US3 (Chat, Reviews & Notificações):** Chat cronológico por agendamento, avaliações mútuas para reservas realizadas com atualização atômica de reputação dos instrutores, serialização estrita de data ISO 8601 UTC ("Z"), cron de lembrete de aula 24h e catálogo de 8 notificações de e-mail integradas ao ciclo de vida.
- **Phase 6 (Polish & Hardening):** Rate-limiting por IP (SlowAPI) no login/registro, injeção de HTTP Security Headers, validação por Magic Bytes (assinaturas binárias hexadecimais), fail-fast de configuração em produção, isolamento resiliente de rede de email/cron e logs estruturados de auditoria de segurança com Trace IDs.

Frontend:

- React 19 + Vite com rotas protegidas por sessão e papel de usuário.
- Fluxos integrados de Login, Busca com mapa interativo (Leaflet) e lista de instrutores aprovados, Agendamento com seletor de slots consecutivos, Gerenciamento de aulas com timelines de status, e painéis de Admin.
- Cliente HTTP com cookies seguros, bearer token e tratamento padronizado.

> [!NOTE]
> O runtime atual de US1 utiliza store em memoria (IdentityStore), adequado para validacao de contratos e testes de fluxo.
> As fases US2/US3 completam persistencia e regras de Booking end-to-end.

## Endpoints do Runtime

Todos os endpoints descritos no contrato OpenAPI estão 100% operacionais no runtime do LinkAuto:

- **Foundation:** `/health`, `/api/v1/foundation/ping`
- **Auth:** `/api/v1/auth/register`, `/api/v1/auth/login`, `/api/v1/auth/refresh`, `/api/v1/auth/password-reset`
- **Users & Profiles:** `/api/v1/users/me`, `/api/v1/users/public-instructors`
- **Slots:** `/api/v1/slots`, `/api/v1/slots/instructor/{id}`
- **Bookings:** `/api/v1/bookings`, `/api/v1/bookings/{id}/cancel`
- **Messages & Reviews:** `/api/v1/bookings/{id}/messages`, `/api/v1/bookings/{id}/reviews`
- **Admin Validation:** `/api/v1/admin/instructors/pending`, `/api/v1/admin/instructors/{id}/approve`, `/api/v1/admin/instructors/{id}/reject`
- **Jobs Cron:** `/api/v1/jobs/booking-reminder`, `/api/v1/jobs/booking-timeout`, `/api/v1/jobs/booking-completion`

## Arquitetura e stack

- Frontend: React 19, Vite, Tailwind CSS 4, React Router, Leaflet (mapas) e Chakra UI (componentes)
- Backend: Python 3.11, FastAPI, SQLAlchemy, Alembic, Pydantic
- Banco: SQLite (dev) e PostgreSQL + PostGIS (alvo de producao)
- Integracoes: AWS S3 (documentos) e AWS SES (notificacoes)

Diagramas disponiveis:

- [docs/diagrams/architecture-overview.svg](docs/diagrams/architecture-overview.svg)
- [docs/diagrams/use-cases-v1.svg](docs/diagrams/use-cases-v1.svg)
- [docs/diagrams/uml-class-diagram-v1.svg](docs/diagrams/uml-class-diagram-v1.svg)
- [docs/diagrams/booking-sequence.svg](docs/diagrams/booking-sequence.svg)

## Estrutura do repositorio

```text
.
├── docs/
├── infra/
├── linkauto-backend/
├── linkauto-frontend/
├── specs/
│   └── 001-user-booking-domains/
└── README.md
```

## Como executar localmente

### Opcao A (recomendada): Docker Compose 🐳

Para iniciar todo o ecossistema (Backend + Frontend + Banco de dados) em segundo plano com um único comando:

```bash
docker compose -f infra/docker-compose.yml up -d
```

> [!TIP]
> 📖 Para uma lista detalhada de comandos Docker, resolução de problemas, execução de testes via container e guia para usuários não-técnicos, consulte o **[Guia Completo de Infraestrutura & Docker (infra/README.md)](infra/README.md)**.

Serviços disponíveis:

- 🌐 **Frontend (Web App):** [http://localhost:5173](http://localhost:5173)
- 🔌 **Backend API (Swagger Docs):** [http://localhost:8000/docs](http://localhost:8000/docs)
- 🩺 **Healthcheck da API:** [http://localhost:8000/health](http://localhost:8000/health)

### Opcao B: Backend e frontend separados (Ambiente Nativo)

Backend:

```bash
cd linkauto-backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000
```

Frontend:

```bash
cd linkauto-frontend
npm install
npm run dev
```

> [!TIP]
> Se voce for validar fluxo de auth com refresh cookie, mantenha frontend e backend rodando com credentials habilitado (ja configurado no cliente HTTP).

## Testes e2e (manual + automatizado)

Preparo inicial (uma vez):

```bash
cd linkauto-frontend
npm install
npm run e2e:install
```

Dependencias de sistema (Linux, quando necessario):

```bash
cd linkauto-frontend
sudo npx playwright install-deps
```

Para Arch Linux (incluindo WSL2 custom), prefira instalar via `yay`/AUR:

```bash
sudo pacman -Syy
yay -S --needed atk at-spi2-core libxcomposite libxdamage libxfixes libxrandr mesa libxkbcommon alsa-lib
```

Executar smoke automatizado (login + busca + solicitacao de agendamento):

```bash
cd linkauto-frontend
npm run e2e
```

Fluxo manual sugerido (com backend e frontend ativos):

1. Abrir `/login`.
2. Registrar um usuario `ALUNO` via endpoint `/api/v1/auth/register` (ou usar conta existente).
3. Autenticar e validar redirecionamento para `/buscar`.
4. Abrir um instrutor em `Agendar`, selecionar 2 slots consecutivos e confirmar navegacao para `/agendamentos`.

Variaveis opcionais para e2e:

- `E2E_BASE_URL` (default: `http://127.0.0.1:5173`)
- `E2E_API_BASE_URL` (default: `http://127.0.0.1:8000/api/v1`)

## Qualidade e testes

Backend (contrato + integracao):

```bash
cd linkauto-backend
. .venv/bin/activate
ruff check .
pytest
```

Frontend (qualidade basica):

```bash
cd linkauto-frontend
npm run lint
npm run build
```

Frontend (e2e smoke):

```bash
cd linkauto-frontend
npm run e2e
```

Coberturas relevantes ja presentes:

- Contrato base de envelope/auth/conflict
- Contrato e fluxo de auth + users/me
- State machine de Booking (dominio)
- Validacao de upload (MIME/10MB)
- Visibilidade de instrutor aprovada por admin

## Roadmap imediato

Itens das próximas fases:

- US3: mensagens por agendamento, reviews após REALIZADA e eventos de notificação completos
- Polish: hardening, regressão em cascata no Booking core e validação final

Regra de execucao por dependencia:

User -> Profile -> Slot -> Booking -> BookingMessage -> Review
