# LinkAuto Backend 🚗💨

Serviço backend desenvolvido com **FastAPI** para a plataforma **LinkAuto**, especializada no agendamento de aulas práticas de trânsito com instrutores autônomos.

---

## 🏛️ Visão Geral da Arquitetura

O backend do LinkAuto foi desenhado com foco nos princípios **SOLID**, **Clean Code** e no padrão **TDD (Test-Driven Development)**, garantindo uma separação clara de preocupações (Separation of Concerns).

```text
linkauto-backend/
├── app/
│   ├── api/             # Camada de Apresentação (HTTP Routers e dependências de Auth/RBAC)
│   ├── core/            # Configurações globais, segurança (JWT/Bcrypt) e conexão de banco
│   ├── domain/          # Entidades puras de domínio e regras de transição de estado
│   ├── models/          # Mapeamento ORM (SQLAlchemy) e chaves primárias baseadas em UUIDv7
│   ├── schemas/         # Validação de Entrada/Saída e schemas de serialização (Pydantic)
│   └── services/        # Regras de Negócio e Casos de Uso (Services e Ports)
├── tests/               # Suíte completa de testes (Unitários, Integração e Contratos)
└── pyproject.toml       # Gerenciamento de dependências e configuração Ruff/Pytest
```

---

## 📅 Domínio de Negócios

### User Story 2 (Booking & Scheduling)
A **US2** introduz a infraestrutura de agendamentos e reserva de slots de horários de instrutores autônomos com as seguintes regras operacionais:
1. **Slots de Aulas:** Cada slot corresponde a **exatamente 1 hora** de aula prática.
2. **Reserva Mínima:** Cada solicitação de agendamento (`Booking`) deve conter no mínimo **2 slots consecutivos** do mesmo instrutor.
3. **Bloqueio de Penalidade (RN04):** Alunos que cancelarem agendamentos confirmados a menos de 24 horas do horário da aula recebem uma suspensão automática de **7 dias**, durante os quais ficam impedidos de realizar novas reservas.
4. **Máquina de Estados de Booking:** O ciclo de vida de uma reserva é estritamente regido por transições de estado controladas:
   - `PENDENTE` ➔ `CONFIRMADA` (pelo instrutor)
   - `PENDENTE`/`CONFIRMADA` ➔ `CANCELADA` (pelo aluno, instrutor ou de forma administrativa)
   - `CONFIRMADA` ➔ `REALIZADA` (conclusão automática)

### User Story 3 (Messages, Reviews & Notifications)
A **US3** implementa ferramentas de comunicação assíncrona, governança de feedbacks e notificações:
1. **Chat de Mensagens:** Permite conversas cronológicas e estruturadas em tempo real entre aluno e instrutor participantes do agendamento.
2. **Avaliações Mútuas:** Alunos e instrutores avaliam o parceiro de 1 a 5 estrelas após reservas concluídas com o status `REALIZADA`. Ao receber uma avaliação do aluno, a média global de estrelas (`rating_avg`) e o total de avaliações (`rating_count`) do instrutor são recalculados de forma atômica no banco de dados.
3. **UTC Datetime Serialization:** Serialização centralizada via Pydantic garantindo o sufixo UTC ISO 8601 `Z` em todas as saídas de data da API.
4. **Catálogo de Notificações por E-mail:** 8 tipos de e-mails em todo o ciclo de vida disparados de forma transparente.
5. **Cron Job de Lembrete:** Rotina automatizada exposta em `/jobs/booking-reminder` que busca reservas confirmadas com início em 24h e envia e-mails preventivos para aluno e instrutor.

---

## 🔒 Hardening e Técnicas de Segurança (`docs/SECURITY_TECHNIQUES.md`)

O projeto segue estritamente as diretrizes da **OWASP Top 10** e os padrões do guia de segurança do LinkAuto:
- **Autenticação Robusta (OWASP A07):** Tokens JWT de ciclo curto (`access_token`) combinados com `refresh_token` trafegados em cookies seguros (`HttpOnly`, `Secure`, `SameSite=Strict`).
- **Defesa Ativa Contra Brute-Force (Rate Limiting):** SlowAPI integrado limitando login (10/min), registro (5/min), refresh (20/min) e redefinição de senha (3/min), com status `429 Too Many Requests`.
- **Prevenção de Mass Assignment (OWASP A01):** Schemas Pydantic fechados (`extra="forbid"`) bloqueando alterações de parâmetros confidenciais (ex: `detran_status`, `rating_avg`).
- **Bloqueio de Privilégios:** Cadastro de novos usuários impede a indicação indevida de papel `ADMIN`.
- **Prevenção de MIME Spoofing:** Validação binária estrita por Magic Bytes (assinaturas binárias hexadecimais) para comprovar a legitimidade de PDFs, JPEGs e PNGs carregados.
- **Prevenção de SQL Injection (OWASP A05):** Remoção de concatenação f-string no BookingLock, utilizando constantes de classe estáticas (`_TABLE_NAME = "slots"`).
- **HTTP Security Headers (OWASP A02):** Injeção sistemática de cabeçalhos de segurança HTTP recomendados pelo OWASP (nosniff, DENY, referrer-policy, etc.).
- **Fail-Fast Config:** Recusa-se a inicializar em produção se o JWT secret padrão for mantido ou se reset automático do SQLite estiver ativo.
- **Traceabilidade Total (Correlation IDs):** Rastreabilidade de requisições de ponta a ponta com propagação de Trace IDs nos cabeçalhos (`X-Correlation-ID`) e logs de auditoria mascarados contra vazamentos.

---

## 🛠️ Como Executar o Backend

### Requisitos Próximos
- Python 3.11
- SQLite3 (Ambiente de Desenvolvimento)

### Configuração do Ambiente Local
1. Crie e ative o ambiente virtual:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. Instale o pacote em modo de desenvolvimento com as dependências adicionais de teste:
   ```bash
   pip install -e ".[dev]"
   ```
3. Inicialize o servidor de desenvolvimento:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

A API estará acessível em `http://localhost:8000` e a documentação interativa Swagger em `http://localhost:8000/docs`.

---

## 🧪 Suíte de Testes e Qualidade

Seguindo o ciclo rigoroso do **TDD**, todos os desenvolvimentos são validados por testes robustos.

### Executar a Suíte de Testes
```bash
# Rodar todos os testes unitários, integração e contrato
pytest

# Rodar com saída detalhada
pytest -v
```

### Verificação de Qualidade e Linter
```bash
# Executar análise estática de código com o Ruff
ruff check .
```
