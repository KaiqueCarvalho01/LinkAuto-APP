# progressTracker

## Contexto

Rastreamento incremental da implementação da feature `001-user-booking-domains`.

## Status por fase

| Fase | Estado | Observação |
|------|--------|------------|
| Phase 1 - Setup | Concluída | T001-T006 finalizadas |
| Phase 2 - Foundational | Concluída | T007-T017 finalizadas e validadas |
| Phase 3 - US1 | Pendente | Bloqueada por dependência |
| Phase 4 - US2 | Pendente | Bloqueada por dependência |
| Phase 5 - US3 | Pendente | Bloqueada por dependência |
| Phase 6 - Polish | Pendente | Bloqueada por dependência |

## Iterações

### Iteração 1

- Criados arquivos de ignore e ajustes de lint ignore.
- Criado esqueleto inicial do backend (app/core/api/models/services/schemas).
- Criado bootstrap de runtime (`infra/docker-compose.yml`) e arquivos `.env.example`.
- Criado cliente HTTP base no frontend (`src/services/httpClient.js` + `config.js`).
- Criado bootstrap Alembic (`alembic/env.py` + `0001_foundation.py`).
- Criado `specs/001-user-booking-domains/compliance.md`.

### Iteração 2

- Implementado `app/models/base.py` com mixins de `uuidv7` (com fallback) e timestamps de auditoria.
- Implementados envelopes/paginação/erros em `app/schemas/common.py`.
- Implementados hashing bcrypt e tokens JWT access/refresh em `app/core/security.py`.
- Implementadas dependências de autenticação e RBAC em `app/api/deps/authn.py` e `authz.py`.
- Implementada abstração de notificação com adapter SES em `app/services/notification_service.py`.
- Implementado core do domínio Booking (matriz de transição + guards) em `app/domain/booking.py`.
- Implementado serviço de reserva atômica first-write-wins em `app/services/booking_lock_service.py`.
- Implementado shell de automações de booking (timeout 24h e +2h completion) em `app/services/booking_scheduler.py`.
- Implementado roteamento fundacional V1 em `app/api/v1/__init__.py` e tratamento padronizado de erro em `app/main.py`.
- Adicionados testes fundacionais de contrato e integração:
  - `tests/contract/test_foundation_contract.py`
  - `tests/integration/test_booking_state_machine.py`
