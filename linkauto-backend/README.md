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

## 📅 Domínio de Negócios: User Story 2 (Booking & Scheduling)

A **US2** introduz a infraestrutura de agendamentos e reserva de slots de horários de instrutores autônomos com as seguintes regras operacionais:

1. **Slots de Aulas:** Cada slot corresponde a **exatamente 1 hora** de aula prática.
2. **Reserva Mínima:** Cada solicitação de agendamento (`Booking`) deve conter no mínimo **2 slots consecutivos** do mesmo instrutor.
3. **Bloqueio de Penalidade (RN04):** Alunos que cancelarem agendamentos confirmados a menos de 24 horas do horário da aula recebem uma suspensão automática de **7 dias**, durante os quais ficam impedidos de realizar novas reservas.
4. **Máquina de Estados de Booking:** O ciclo de vida de uma reserva é estritamente regido por transições de estado controladas:
   - `PENDENTE` ➔ `CONFIRMADA` (pelo instrutor)
   - `PENDENTE`/`CONFIRMADA` ➔ `CANCELADA` (pelo aluno, instrutor ou de forma administrativa)
   - `CONFIRMADA` ➔ `REALIZADA` (conclusão automática)

---

## 🔒 Hardening e Técnicas de Segurança (`docs/SECURITY_TECHNIQUES.md`)

O projeto segue as diretrizes da **OWASP Top 10** para blindagem da API:
- **Autenticação Robusta:** Utilização de tokens JWT de ciclo curto (`access_token`) combinados com `refresh_token` trafegados em cookies seguros (`HttpOnly`, `Secure`, `SameSite=Strict`).
- **Prevenção de Mass Assignment:** Schemas Pydantic fechados (`extra="forbid"`) garantindo que apenas campos legítimos sejam processados.
- **Transações Atômicas (First-Write-Wins):** O `BookingService` reserva os slots de forma atômica no banco de dados. Caso ocorra concorrência, o primeiro a registrar bloqueia os demais, evitando sobreposição de agendamento (double-booking).
- **Controle de Acesso RBAC:** Dependências centrais do FastAPI garantem que apenas usuários autenticados e com os papéis devidos (`ALUNO`, `INSTRUTOR` ou `ADMIN`) acessem endpoints protegidos.

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
