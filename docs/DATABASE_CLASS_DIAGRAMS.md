# 🏛️ LinkAuto — Diagramas de Classe dos Schemas de Banco de Dados

> Documento canônico de arquitetura dos modelos de dados e persistência do LinkAuto.  
> **ORM & Framework:** SQLModel 0.0.48 / SQLAlchemy 2.0  
> **Chaves Primárias & Auditoria:** UUIDv7 em string (36 caracteres) e timestamps UTC automáticos.  
> **Bancos Homologados:** SQLite em desenvolvimento/testes automatizados e PostgreSQL + PostGIS em produção.

---

## 📑 Sumário

1. [Padrões Arquiteturais de Persistência](#1-padrões-arquiteturais-de-persistência)
2. [Diagrama 1: Visão Geral de Entidades e Relacionamentos](#2-diagrama-1-visão-geral-de-entidades-e-relacionamentos)
3. [Diagrama 2: Domínio de Identidade & Perfis](#3-diagrama-2-domínio-de-identidade--perfis)
4. [Diagrama 3: Domínio de Agendamentos & Agenda de Slots](#4-diagrama-3-domínio-de-agendamentos--agenda-de-slots)
5. [Diagrama 4: Domínio de Governança, Comunicação & Reputação](#5-diagrama-4-domínio-de-governança-comunicação--reputação)
6. [Instruções de Manutenção e Compilação (Mermaid Studio)](#6-instruções-de-manutenção-e-compilação-mermaid-studio)

---

## 1. Padrões Arquiteturais de Persistência

Os modelos do LinkAuto residem no pacote [`linkauto-backend/app/models/`](../linkauto-backend/app/models/) e seguem os princípios:

- **Herança Base (`base.py`):**
  - `AuditTimestampsMixin`: Colunas não nulas `created_at` e `updated_at` com fuso horário UTC obrigatório.
  - `AuditUUIDBase`: Herda de `AuditTimestampsMixin` e introduz chave primária `id: str` gerada via `generate_uuid7()` (UUIDv7 ordenável no tempo, com fallback seguro para UUIDv4).
- **Tipagem Estrita Python & SQL:** Tipos primitivos tipados nativamente via Pydantic/SQLModel (`str`, `int`, `float`, `Decimal`, `bool`, `datetime`) e convertidos com fidelidade para colunas relacionais.
- **Blindagem LGPD & Slugs Públicos:** Os perfis de aluno e instrutor possuem a coluna `slug` única e indexada para permitir navegação pública sem vazar ou expor UUIDs de identificação do sistema.

---

## 2. Diagrama 1: Visão Geral de Entidades e Relacionamentos

Visão macro da estrutura de herança das entidades e os vínculos relacionais entre todas as 11 tabelas do sistema.

![Visão Geral das Classes do Banco](./diagrams/database-overview-class.svg)

### Código Mermaid (.mmd)

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#1A6DB5', 'primaryTextColor': '#ffffff', 'primaryBorderColor': '#124E87', 'lineColor': '#94a3b8', 'secondaryColor': '#3EAA5B', 'tertiaryColor': '#F59E0B', 'background': '#ffffff', 'mainBkg': '#f8fafc', 'nodeBorder': '#cbd5e1', 'clusterBkg': '#f1f5f9', 'clusterBorder': '#e2e8f0', 'titleColor': '#111827', 'edgeLabelBackground': '#ffffff', 'textColor': '#1e293b'}}}%%
classDiagram
    direction TB

    class AuditTimestampsMixin {
        <<mixin>>
        +datetime created_at
        +datetime updated_at
    }

    class AuditUUIDBase {
        <<base>>
        +str id [PK - UUIDv7]
    }

    class User {
        <<table: users>>
        +str id [PK]
        +str email [UNIQUE]
        +str password_hash
        +list~str~ roles [JSON]
        +bool is_active
    }

    class StudentProfile {
        <<table: student_profiles>>
        +str user_id [PK, FK]
        +str slug [UNIQUE]
        +str full_name
        +str phone
        +str city
        +str state
        +str license_type
        +str avatar_url
    }

    class InstructorProfile {
        <<table: instructor_profiles>>
        +str user_id [PK, FK]
        +str slug [UNIQUE]
        +str full_name
        +str phone
        +str city
        +str state
        +str bio
        +list~str~ specialties [JSON]
        +Decimal price_per_hour
        +str detran_status
        +int action_radius_km
        +float latitude
        +float longitude
        +float rating_avg
        +int rating_count
        +bool is_active
    }

    class RefreshToken {
        <<table: refresh_tokens>>
        +str id [PK]
        +str jti [UNIQUE]
        +str user_id [FK]
        +str family_id
        +datetime expires_at
        +datetime used_at
        +datetime revoked_at
        +str replaced_by_jti
    }

    class InstructorDocument {
        <<table: instructor_documents>>
        +str id [PK]
        +str instructor_id [FK]
        +str reviewed_by [FK]
        +str detran_credential_url
        +str criminal_record_url
        +datetime uploaded_at
        +datetime reviewed_at
        +str review_status
        +str review_reason
    }

    class Slot {
        <<table: slots>>
        +str id [PK]
        +str instructor_id [FK]
        +datetime starts_at
        +datetime ends_at
        +str status
    }

    class Booking {
        <<table: bookings>>
        +str id [PK]
        +str student_id [FK]
        +str instructor_id [FK]
        +str status
        +str location_description
        +Decimal latitude
        +Decimal longitude
        +datetime confirmed_at
        +datetime cancelled_at
        +str cancelled_by
        +str cancellation_reason
        +bool reminder_sent
    }

    class BookingSlot {
        <<table: booking_slots>>
        +str id [PK]
        +str booking_id [FK]
        +str slot_id [UNIQUE, FK]
    }

    class StudentPenalty {
        <<table: student_penalties>>
        +str id [PK]
        +str student_id [FK]
        +datetime blocked_until
        +str reason
    }

    class BookingStatusOverride {
        <<table: booking_status_overrides>>
        +str id [PK]
        +str booking_id [FK]
        +str admin_id
        +str from_status
        +str to_status
        +str reason
    }

    class Review {
        <<table: reviews>>
        +str id [PK]
        +str booking_id [FK]
        +str reviewer_id [FK]
        +str reviewed_id [FK]
        +int rating
        +str comment
    }

    class BookingMessage {
        <<table: booking_messages>>
        +str id [PK]
        +str booking_id [FK]
        +str sender_id [FK]
        +str content
    }

    AuditTimestampsMixin <|-- AuditUUIDBase
    AuditUUIDBase <|-- User
    AuditTimestampsMixin <|-- StudentProfile
    AuditTimestampsMixin <|-- InstructorProfile
    AuditUUIDBase <|-- RefreshToken
    AuditUUIDBase <|-- InstructorDocument
    AuditUUIDBase <|-- Slot
    AuditUUIDBase <|-- Booking
    AuditUUIDBase <|-- BookingSlot
    AuditUUIDBase <|-- StudentPenalty
    AuditUUIDBase <|-- BookingStatusOverride
    AuditUUIDBase <|-- Review
    AuditUUIDBase <|-- BookingMessage

    User "1" *-- "0..1" StudentProfile : owns
    User "1" *-- "0..1" InstructorProfile : owns
    User "1" o-- "*" RefreshToken : sessions
    InstructorProfile "1" o-- "*" InstructorDocument : verification
    InstructorProfile "1" o-- "*" Slot : agenda
    StudentProfile "1" o-- "*" Booking : books
    InstructorProfile "1" o-- "*" Booking : provides
    Booking "1" *-- "1..*" BookingSlot : reserves
    Slot "1" -- "0..1" BookingSlot : locked_in
    StudentProfile "1" o-- "*" StudentPenalty : penalties
    Booking "1" o-- "*" BookingStatusOverride : overrides
    Booking "1" o-- "0..2" Review : evaluations
    Booking "1" o-- "*" BookingMessage : messages
```

---

## 3. Diagrama 2: Domínio de Identidade & Perfis

Representa a camada de autenticação, contas, rotação de refresh tokens JWT, perfis especializados e conformidade regulatória (DETRAN).

![Diagrama de Identidade e Perfis](./diagrams/identity-domain-class.svg)

### Classes e Enums do Domínio

| Entidade / Enum | Arquivo Fonte | Responsabilidade |
|---|---|---|
| `User` | [`user.py`](../linkauto-backend/app/models/user.py) | Conta base com credenciais criptografadas (bcrypt), email único e lista de papéis (roles). |
| `StudentProfile` | [`user.py`](../linkauto-backend/app/models/user.py) | Perfil do aluno, categoria de CNH de interesse e slug público de reputação. |
| `InstructorProfile` | [`user.py`](../linkauto-backend/app/models/user.py) | Perfil do instrutor com dados geográficos, valor hora/aula, raio de atuação e status DETRAN. |
| `RefreshToken` | [`refresh_token.py`](../linkauto-backend/app/models/refresh_token.py) | Tokens de renovação com rotação estrita e detecção de reutilização por `family_id`. |
| `InstructorDocument` | [`instructor_document.py`](../linkauto-backend/app/models/instructor_document.py) | Documentos comprobatórios (credencial DETRAN e antecedentes) validados pelo administrador (RN01). |
| `UserRole` | [`user.py`](../linkauto-backend/app/models/user.py) | Enum de papéis: `ALUNO`, `INSTRUTOR`, `ADMIN`. |
| `LicenseType` | [`user.py`](../linkauto-backend/app/models/user.py) | Categorias de habilitação: `NENHUMA`, `A`, `B`, `AB`, `C`, `D`, `E`, `EM_PROCESSO`. |
| `DetranStatus` | [`user.py`](../linkauto-backend/app/models/user.py) | Estados de homologação de credencial: `PENDENTE`, `APROVADO`, `REJEITADO`. |

---

## 4. Diagrama 3: Domínio de Agendamentos & Agenda de Slots

Representa a máquina de estados das aulas, amarração de blocos de agenda, bloqueio de horários e regras disciplinares.

![Diagrama de Agendamentos e Slots](./diagrams/booking-domain-class.svg)

### Regras de Negócio Implementadas

1. **Grade de Horários (`Slot`):** Slots individuais representam blocos indivisíveis de 1 hora.
2. **Reserva Mínima (RN03):** Cada agendamento (`Booking`) deve conter no mínimo 2 slots contíguos (2 horas consecutivas).
3. **Bloqueio e Unicidade (`BookingSlot`):** A tabela associativa possui restrição `UNIQUE(slot_id)`, impedindo matematicamente qualquer condição de corrida ou reserva duplicada do mesmo horário.
4. **Política de Cancelamento e Penalidade (RN04):**
   - Cancelamento permitido com antecedência mínima de 24 horas.
   - Cancelamentos com menos de 24 horas geram registro em `StudentPenalty`, bloqueando o aluno de novos agendamentos por 7 dias (`blocked_until`).
5. **Trilha de Auditoria (`BookingStatusOverride`):** Modificações forçadas por administradores registram o estado anterior, novo estado e justificativa.

---

## 5. Diagrama 4: Domínio de Governança, Comunicação & Reputação

Representa os canais de interação assíncrona entre as partes de uma reserva e o sistema de avaliação mútua e reputação.

![Diagrama de Governança e Reputação](./diagrams/governance-domain-class.svg)

### Integridade e Blindagem

- **Mensagens (`BookingMessage`):** Restritas às partes participantes de uma reserva confirmada (`booking_id`), com indexação otimizada por `(booking_id, created_at)` para paginação rápida.
- **Avaliações (`Review`):**
  - Avaliação bilateral permitida apenas após a aula atingir o status `REALIZADA`.
  - Garantida por `UniqueConstraint("booking_id", "reviewer_id")`, impedindo que uma mesma parte avalie mais de uma vez a mesma reserva.
  - Nota de 1 a 5 estrelas com recálculo automático de `rating_avg` e `rating_count` no perfil do instrutor.

---

## 6. Instruções de Manutenção e Compilação (Mermaid Studio)

Todos os diagramas foram gerados e validados com as ferramentas do **Mermaid Studio**. Para recompilar ou gerar novas versões após alterações nos modelos:

```bash
# Definir diretório de dependências do Mermaid Studio
export MERMAID_STUDIO_DIR=$HOME/.local/share/mermaid-studio

# Re-renderizar diagramas individuais para SVG
node ~/.gemini/skills/mermaid-studio/scripts/render.mjs \
  --input docs/diagrams/database-overview-class.mmd \
  --output docs/diagrams/database-overview-class.svg

node ~/.gemini/skills/mermaid-studio/scripts/render.mjs \
  --input docs/diagrams/identity-domain-class.mmd \
  --output docs/diagrams/identity-domain-class.svg

node ~/.gemini/skills/mermaid-studio/scripts/render.mjs \
  --input docs/diagrams/booking-domain-class.mmd \
  --output docs/diagrams/booking-domain-class.svg

node ~/.gemini/skills/mermaid-studio/scripts/render.mjs \
  --input docs/diagrams/governance-domain-class.mmd \
  --output docs/diagrams/governance-domain-class.svg
```
