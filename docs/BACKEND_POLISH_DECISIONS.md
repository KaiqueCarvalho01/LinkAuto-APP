# Backend Polish & Hardening — Decisões Técnicas (Phase 6)

> **Branch**: `feature/polish-backend`
> **Baseline**: 95 testes verdes, linter Ruff 100% limpo, structured logging com correlation ID.
> **Referências**: `docs/SECURITY_TECHNIQUES.md`, OWASP Top 10:2025, OWASP API Security Top 10:2023.

> [!IMPORTANT]
> Este documento fundamenta **cada decisão** de hardening com:
> (1) evidência concreta no código atual,
> (2) risco catalogado no `SECURITY_TECHNIQUES.md`,
> (3) justificativa técnica, e
> (4) critério mensurável de sucesso (before → after).

---

## Índice de Decisões

| ID | Prioridade | Título | OWASP | Seção |
|----|-----------|--------|-------|-------|
| D01 | P0 | Bloquear ADMIN no registro público | A01, A07 | §1 |
| D02 | P0 | Sanitizar `.env.example` | A02, A03 | §2 |
| D03 | P1 | Fechar schema de profile update (mass assignment) | A01, API3 | §3 |
| D04 | P1 | Security headers middleware | A02 | §4 |
| D05 | P1 | Secure-by-default config (fail-fast em produção) | A02 | §5 |
| D06 | P1 | Elevar validação de upload (magic bytes) | A05, A10 | §6 |
| D07 | P2 | Logging estruturado de eventos de segurança | A09 | §7 |
| D08 | P2 | Hardening do SQL em booking_lock_service | A05 | §8 |
| D09 | P2 | Rate limiting com slowapi | A07, API4 | §9 |
| D10 | P2 | Testes orientados a abuso | A01, A07 | §10 |
| D11 | P1 | Resiliência do NotificationService | A10 | §11 |
| D12 | P2 | N+1 queries no BookingService | — | §12 |
| D13 | P2 | Resiliência per-item no scheduler | A10 | §13 |

---

## §1 — D01: Bloquear ADMIN no registro público

### Evidência

```python
# app/api/v1/auth.py:15-18
class RegisterRequest(BaseModel):
    email: str = Field(min_length=3)
    password: str = Field(min_length=8)
    roles: list[str] = Field(min_length=1)  # ← ACEITA qualquer role
```

```python
# app/services/auth_service.py:37-38
def register(self, *, email: str, password: str, roles: list[str]) -> UserRecord:
    user = self._store.create_user(email=email, password_hash=hash_password(password), roles=roles)
    # ← Nenhuma validação de allowlist
```

### Risco

`SECURITY_TECHNIQUES.md §5.1` — Severidade **CRÍTICA**. Um usuário externo pode criar conta
com papel `ADMIN` enviando `{"roles": ["ADMIN"]}` no body.

### Decisão

Implementar **allowlist estrita** no `RegisterRequest` via Pydantic `field_validator`:
- Papéis permitidos no registro público: `ALUNO`, `INSTRUTOR`.
- Tentativa de incluir `ADMIN` → retorna `400 Bad Request` com código `FORBIDDEN_ROLE`.
- Criação de admins exclusivamente via seed de banco ou endpoint administrativo protegido (futuro).

### Justificativa

Defesa em profundidade: validar no schema (primeira barreira) **e** no service (segunda barreira).
Custo de implementação: ~15 linhas. Impacto de não fazer: escalação de privilégio total.

### Critério de Sucesso

| Before | After |
|--------|-------|
| `POST /auth/register {"roles":["ADMIN"]}` → `201 Created` | `POST /auth/register {"roles":["ADMIN"]}` → `400 Bad Request` |
| 0 testes validando bloqueio | ≥2 testes (contrato + integração) provando o bloqueio |

---

## §2 — D02: Sanitizar `.env.example`

### Evidência

```ini
# .env.example:7-14
JWT_SECRET=YOUR_JWT_SECRET_PLACEHOLDER
AWS_ACCESS_KEY_ID=YOUR_AWS_ACCESS_KEY_ID_PLACEHOLDER
AWS_SECRET_ACCESS_KEY=YOUR_AWS_SECRET_ACCESS_KEY_PLACEHOLDER
S3_BUCKET=linkauto--fatec-2026
SES_FROM_EMAIL=gabrieldnsilva@gmail.com
```

### Risco

`SECURITY_TECHNIQUES.md §5.2` — Severidade **BAIXA (No Git) / MÉDIA (Local)**.
A regra `.env*` presente no `.gitignore` garante que arquivos contendo segredos como `.env.example` ou `.env` locais **não são subidos** para o repositório remoto Git. Contudo, em termos de boas práticas de design e onboarding de novos desenvolvedores locais, manter credenciais fictícias no template padrão do projeto local é desejável para mitigar riscos de vazamento acidental fora da regra.

### Decisão

1. Manter placeholders descritivos (ex: `your-jwt-secret-here`) para quaisquer novos templates de exemplo distribuídos.
2. Preservar as configurações funcionais de teste locais do usuário no `.env.example` atual, uma vez que sua exclusão do controle de versão pelo `.gitignore` está validada e segura de forma robusta.

### Justificativa

OWASP A02/A03 orienta que segredos nunca estejam hardcoded. A verificação do `.gitignore` confirma que o projeto está 100% blindado contra vazamentos involuntários de arquivos `.env*` no GitHub, mantendo segredos restritos ao ambiente local seguro.

### Critério de Sucesso

| Before | After |
|--------|-------|
| Temor de vazamento remoto de chaves locais | Validação do `.gitignore` bloqueando envs remotos e segurança garantida |

---

## §3 — D03: Fechar schema de profile update

### Evidência

```python
# app/api/v1/users.py:14-15
class UserMePatchRequest(BaseModel):
    model_config = ConfigDict(extra="allow")  # ← MASS ASSIGNMENT
```

```python
# app/api/v1/users.py:40
user_payload = profile_service.update_me(current_user.user_id, payload.model_dump())
# ← Todo campo extra é repassado diretamente
```

### Risco

`SECURITY_TECHNIQUES.md §5.6` — Severidade **MÉDIA/ALTA**. Em evoluções futuras, campos sensíveis de status de aprovação administrativa ou pontuações de avaliações (`detran_status`, `rating_avg`, `rating_count`) poderiam ser manipulados via injeção direta no payload do PATCH do perfil caso o schema permaneça aberto.

### Decisão

Substituir `extra="allow"` por esquemas aninhados explícitos e fechados com `extra="forbid"`, isolando o escopo editável de cada tipo de perfil de forma cirúrgica. Os campos permitidos para edição no `UserMePatchRequest` são todos os legítimos de cadastro, **exceto** `detran_status`, `rating_avg` e `rating_count`:

```python
class StudentProfilePatch(BaseModel):
    model_config = ConfigDict(extra="forbid")
    full_name: str | None = None
    phone: str | None = None
    city: str | None = None
    state: str | None = None
    license_type: str | None = None
    avatar_url: str | None = None

class InstructorProfilePatch(BaseModel):
    model_config = ConfigDict(extra="forbid")
    full_name: str | None = None
    phone: str | None = None
    city: str | None = None
    state: str | None = None
    bio: str | None = None
    specialties: list[str] | None = None
    price_per_hour: float | None = None
    avatar_url: str | None = None
    action_radius_km: int | None = None
    latitude: float | None = None
    longitude: float | None = None
    is_active: bool | None = None

class UserMePatchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    student_profile: StudentProfilePatch | None = None
    instructor_profile: InstructorProfilePatch | None = None
```

Qualquer tentativa de passar outros campos (ex: `is_admin` ou `detran_status` direto) no JSON de atualização é rejeitada de imediato no nível do FastAPI com `422 Unprocessable Entity` (ou `400 Bad Request` conforme o handler).

### Justificativa

Princípio de menor privilégio aplicado a dados. Schema fechado é a **primeira barreira** contra mass assignment (OWASP API3). Bloqueia-se a alteração de campos críticos como `detran_status` e métricas de `rating` sem restringir a flexibilidade de o usuário atualizar seus próprios dados de contato e localização.

### Critério de Sucesso

| Before | After |
|--------|-------|
| `PATCH /users/me {"instructor_profile":{"detran_status":"APROVADO"}}` → Aceita alteração do status administrativo! | → Retorna `422 Unprocessable Entity`/`400 Bad Request` |
| `PATCH /users/me {"instructor_profile":{"rating_avg":5.0}}` → Aceita injeção direta de ratings! | → Retorna erro de validação de campo não permitido |
| Schema aberto com `extra="allow"` | Schema fechado com `extra="forbid"` e campos aninhados seguros |

---

## §4 — D04: Security headers middleware

### Evidência

```python
# app/main.py — Nenhum middleware de security headers
# Apenas CORSMiddleware e CorrelationIDMiddleware registrados
```

### Risco

`SECURITY_TECHNIQUES.md §5.9` — Severidade **MÉDIA**. Ausência de HSTS, CSP,
X-Content-Type-Options, Referrer-Policy e Permissions-Policy aumenta superfície de ataque.

### Decisão

Criar `SecurityHeadersMiddleware` em `app/core/middleware.py`:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: camera=(), microphone=(), geolocation=()`
- `Cache-Control: no-store` para respostas de API
- CSP e HSTS ficam para o reverse proxy (Nginx/CloudFront) — documentar essa decisão.

### Justificativa

Headers no nível da aplicação cobrem o cenário de acesso direto ao backend (dev, staging).
HSTS e CSP completos são responsabilidade do reverse proxy porque dependem de configuração
de certificado TLS e domínio, que estão fora do escopo do app Python.

### Critério de Sucesso

| Before | After |
|--------|-------|
| `curl -I /health` → sem headers de segurança | `curl -I /health` → 5 security headers presentes |
| 0 testes | ≥1 teste de contrato validando presença dos headers |

---

## §5 — D05: Secure-by-default config

### Evidência

```python
# app/core/config.py:19
jwt_secret: str = Field(default="change-me", alias="JWT_SECRET")
# ← Não há validação em produção
```

```python
# app/core/config.py:13
reset_sqlite_on_startup: bool = Field(default=True, alias="RESET_SQLITE_ON_STARTUP")
# ← Em produção, reset=true apagaria o banco
```

### Risco

`SECURITY_TECHNIQUES.md §7.4` — "Falhar startup em produção se JWT_SECRET=change-me".
Configuração insegura não deve ser silenciosa.

### Decisão

Adicionar `@model_validator(mode="after")` na classe `Settings`:
1. Se `app_env == "production"` e `jwt_secret == "change-me"` → `raise ValueError`.
2. Se `app_env == "production"` e `reset_sqlite_on_startup == True` → `raise ValueError`.
3. Se `app_env == "production"` e `cors_origins` contém `localhost` → emitir `warning` no log.

### Justificativa

Fail-fast é mais seguro que fail-silent. Uma aplicação que sobe em produção com JWT secret
padrão permite forjar tokens de qualquer usuário (incluindo ADMIN). O custo de um validator
é ~8 linhas; o custo de não ter é **comprometimento total da autenticação**.

### Critério de Sucesso

| Before | After |
|--------|-------|
| `APP_ENV=production JWT_SECRET=change-me` → app sobe normalmente | → app **falha no startup** com mensagem clara |
| 0 testes | ≥2 testes unitários validando fail-fast |

---

## §6 — D06: Validação de upload por magic bytes

### Evidência

```python
# app/services/instructor_document_service.py:37-41
@staticmethod
async def _read_and_validate(upload: UploadFile) -> bytes:
    if upload.content_type not in ALLOWED_MIME_TYPES:  # ← Header declarado pelo cliente
        raise DocumentValidationError(...)
    content = await upload.read()
    # ← Sem verificação do conteúdo real (magic bytes)
```

### Risco

`SECURITY_TECHNIQUES.md §5.5` — Severidade **ALTA**. Um atacante pode enviar um executável
malicioso declarando `content_type: "application/pdf"`.

### Decisão

Adicionar verificação de **magic bytes** após `await upload.read()`:

| MIME | Magic Bytes (hex) |
|------|-------------------|
| `application/pdf` | `%PDF` (25 50 44 46) |
| `image/jpeg` | `FF D8 FF` |
| `image/png` | `89 50 4E 47 0D 0A 1A 0A` |

Implementar como dicionário constante em `instructor_document_service.py`.
**Não** adicionar dependência externa (como `python-magic`) — a verificação por header bytes
é determinística e suficiente para V1.

### Justificativa

Verificar magic bytes é defesa em profundidade (defense in depth) sem custo de dependência.
`python-magic` exige `libmagic` (C library), que complica builds Docker e CI.
A verificação manual dos primeiros bytes é técnica consagrada
(OWASP File Upload Cheat Sheet) e cobre os 3 formatos aceitos com 100% de confiabilidade.

### Critério de Sucesso

| Before | After |
|--------|-------|
| Upload com `content_type="application/pdf"` + conteúdo binário qualquer → aceito | → `400 Bad Request` com código `INVALID_FILE_CONTENT` |
| 0 testes de magic bytes | ≥3 testes (um por MIME + 1 para MIME falso) |

---

## §7 — D07: Logging estruturado de eventos de segurança

### Evidência

```python
# app/core/logging.py — Existe CorrelationIDMiddleware e CorrelationIDFilter
# Porém NENHUM evento de segurança é logado explicitamente nos services
```

```python
# app/api/v1/auth.py:68-73 — Login failure apenas levanta HTTPException
# Sem log de "auth.login.failure" com email/IP
```

### Risco

`SECURITY_TECHNIQUES.md §5.8` e `§6.7` — Severidade **MÉDIA/ALTA**. Incidentes de segurança
ficam sem trilha de auditoria operacional. Brute force invisível.

### Decisão

Criar `app/core/security_logger.py` com funções utilitárias:
- `log_auth_success(email, ip)` → `logger.info` com `event=auth.login.success`
- `log_auth_failure(email, ip)` → `logger.warning` com `event=auth.login.failure`
- `log_forbidden(user_id, resource, ip)` → `logger.warning` com `event=authz.forbidden`
- `log_upload_rejected(user_id, reason)` → `logger.warning` com `event=upload.rejected`
- `log_admin_action(admin_id, action, target_id)` → `logger.info` com `event=admin.action`

**Regras de mascaramento**: nunca logar senhas, tokens completos, ou connection strings.
Logar apenas os 4 últimos caracteres de tokens (`...a2f8`).

### Justificativa

A infraestrutura de correlação ID já existe (`CorrelationIDFilter`). Falta apenas
**emitir** os eventos. O log estruturado com campos semânticos (`event=`, `email=`, `ip=`)
permite filtragem e alerting em qualquer stack de observabilidade (ELK, CloudWatch, Datadog).

### Critério de Sucesso

| Before | After |
|--------|-------|
| Login failure → apenas HTTP 401 retornado | → HTTP 401 + log `WARNING [auth.login.failure]` com correlation_id |
| Admin approve → nenhum registro | → log `INFO [admin.action]` com admin_id e instructor_id |
| 0 eventos de segurança logados | ≥5 categorias de eventos cobertas |

---

## §8 — D08: Hardening do SQL em booking_lock_service

### Evidência

```python
# app/services/booking_lock_service.py:62-68
statement = text(
    f"""
    UPDATE {self._table_name}        # ← f-string com table_name
    SET status = :reserved_status
    WHERE id IN :slot_ids
      AND status = :available_status
    """
).bindparams(bindparam("slot_ids", expanding=True))
```

### Risco

`SECURITY_TECHNIQUES.md §5.11` — Severidade **MÉDIA**. Hoje `table_name` tem valor fixo
interno (`"slots"`), mas se futuramente for configurável por entrada externa, torna-se
vetor de SQL injection.

### Decisão

Substituir `table_name` por **constante de classe** não configurável:
```python
_TABLE_NAME: str = "slots"  # Constante, não aceita input externo
```
Remover o parâmetro `table_name` do `__init__`. Se necessário futuramente, validar
contra allowlist (`{"slots"}`).

### Justificativa

Princípio YAGNI + defense in depth: não expor configuração que não precisa existir.
Custo: ~5 linhas removidas. Benefício: elimina vetor latente permanentemente.

### Critério de Sucesso

| Before | After |
|--------|-------|
| `table_name` é parâmetro configurável no `__init__` | `_TABLE_NAME` é constante interna |
| f-string usa variável de instância | f-string usa constante de classe |

---

## §9 — D09: Rate limiting com slowapi

### Evidência

```python
# app/main.py — Nenhum middleware de rate limiting
# app/api/v1/auth.py — Login, register, refresh sem limites
```

### Risco

`SECURITY_TECHNIQUES.md §5.4` — Severidade **ALTA**. Sem rate limit, os endpoints de
autenticação são vulneráveis a brute force, credential stuffing e DoS.

### Decisão

Adicionar `slowapi` (wrapper de `limits` sobre Starlette) com limites por IP:
- `/auth/login`: 10 req/min
- `/auth/register`: 5 req/min
- `/auth/refresh`: 20 req/min
- `/auth/password-reset`: 3 req/min
- Upload de documentos: 5 req/min
- Default global: 100 req/min

`slowapi` usa armazenamento em memória por padrão (suficiente para V1 single-instance).
Para produção multi-instance, migrar para Redis backend (documentar como evolução futura).

### Justificativa

`slowapi` é a solução consolidada para FastAPI/Starlette com 2k+ stars, mantida ativamente,
e não exige dependência externa de armazenamento para V1. Alternativas como middleware
customizado seriam reinventar a roda (viola regra constitucional: "Não reinvente a roda").

### Critério de Sucesso

| Before | After |
|--------|-------|
| `for i in range(100): POST /auth/login` → todas retornam 401 | → Após 10ª requisição, retorna `429 Too Many Requests` |
| 0 testes | ≥2 testes validando rate limit em login e register |

---

## §10 — D10: Testes orientados a abuso

### Evidência

`SECURITY_TECHNIQUES.md §7.5` lista cenários de abuso não cobertos pelos testes atuais:
- Usuário comum tentando endpoint admin → coberto parcialmente
- Usuário tentando alterar role via PATCH → **não coberto**
- Upload com MIME falso → **não coberto** (magic bytes)
- Payload com campos extras → **não coberto**
- Registro com role ADMIN → **não coberto**

### Decisão

Criar `tests/security/test_abuse_scenarios.py` com cenários:
1. `test_register_with_admin_role_is_blocked`
2. `test_patch_profile_rejects_extra_fields`
3. `test_upload_with_fake_mime_is_rejected`
4. `test_student_cannot_access_admin_endpoints`
5. `test_security_headers_are_present`
6. `test_rate_limit_on_login`

### Justificativa

Testes de abuso são **documentação executável** das barreiras de segurança. Garantem que
hardening não regride em refatorações futuras. O investimento é ~100 linhas de teste com
retorno permanente em segurança de regressão.

### Critério de Sucesso

| Before | After |
|--------|-------|
| 0 testes dedicados a abuso | ≥6 testes em `tests/security/` |
| Cenários de segurança dependem de revisão manual | Cenários automatizados no CI |

---

## §11 — D11: Resiliência do NotificationService

### Evidência

```python
# app/services/notification_service.py — dispatch() chama self._email_gateway.send()
# Sem try/except. Se SES falhar (network, quota, email inválido),
# a exceção propaga e crasha o fluxo de booking/review que disparou.
```

### Risco

Severidade **P1**. Uma falha de rede ao enviar email de notificação
faz um `POST /bookings` retornar 500, mesmo que o booking foi criado com sucesso.
O efeito colateral (email) não pode derrubar a operação principal.

### Decisão

Envolver `self._email_gateway.send()` em `try/except Exception`:
1. Em caso de falha, logar `WARNING` com `event=notification.dispatch.failure`.
2. Retornar `NotificationDispatchResult` com `success=False` e mensagem.
3. **Nunca** permitir que falha de notificação aborte a transação de negócio.

### Justificativa

Notificações são **efeitos colaterais assíncronos** por natureza. Em arquiteturas
maduras, usam-se filas (SQS, RabbitMQ). Para V1, o `try/except` é a solução KISS
que previne cascata de falhas sem adicionar infraestrutura.

### Critério de Sucesso

| Before | After |
|--------|-------|
| SES offline → `POST /bookings` retorna 500 | → `POST /bookings` retorna 201 + log WARNING |
| ≥1 teste simulando falha de gateway | Gateway mock que levanta Exception → booking persiste |

---

## §12 — D12: Corrigir N+1 queries

### Evidência

```python
# app/services/booking_service.py — cancel_booking():
# for link in booking.slots:  # lazy-loaded
#     slot = self._db.query(Slot).filter(Slot.id == link.slot_id).first()  # N queries
```

```python
# app/services/admin_validation_service.py — list_instructors():
# items = [self._profile_service.get_me(instructor.id) for instructor in instructors[start:end]]
# ← N queries por página
```

### Risco

Severidade **P2**. Degradação de performance proporcional ao número de slots/instrutores.
Para V1 com poucos dados é imperceptível, mas escala mal.

### Decisão

1. `cancel_booking()`: Substituir loop por `Slot.id.in_(slot_ids)` único.
2. `list_instructors()`: Usar `User.id.in_(instructor_ids)` com batch query.
3. **Não** adicionar eager loading global — lazy loading é correto para a maioria dos
   endpoints. Otimizar apenas os hotpaths identificados.

### Justificativa

YAGNI para eager loading geral. Fix cirúrgico nos 2 pontos identificados
reduz queries de O(n) para O(1) sem mudança arquitetural.

### Critério de Sucesso

| Before | After |
|--------|-------|
| `cancel_booking` com 5 slots → 5 queries individuais | → 1 query com `IN` clause |
| `list_instructors` com page_size=20 → 20 queries | → 1 query batch |

---

## §13 — D13: Resiliência per-item no scheduler

### Evidência

```python
# app/services/booking_scheduler.py — processo de timeout/completion
# Itera bookings e transiciona estado.
# Se uma transição falhar, aborta todo o batch.
```

### Risco

Severidade **P2**. Um booking corrompido impede processamento de todos os
bookings subsequentes no lote.

### Decisão

Envolver cada transição individual em `try/except`:
1. Logar `WARNING` para falhas individuais com booking_id.
2. Continuar processando os demais.
3. Retornar contador de `processed` e `failed`.

### Justificativa

Princípio de isolamento de falhas. O scheduler é um job batch — falha parcial
é preferível a falha total.

### Critério de Sucesso

| Before | After |
|--------|-------|
| 1 booking inválido → batch inteiro aborta | → booking inválido logado, demais processados |
| Retorno: sucesso/falha total | Retorno: `{"processed": N, "failed": M}` |

---

## Decisões EXPLICITAMENTE NÃO TOMADAS (YAGNI)

> [!NOTE]
> As seguintes melhorias foram **avaliadas e explicitamente descartadas** para a V1 da aplicação baseando-se no princípio YAGNI, de modo a evitar carga cognitiva e infraestrutura adicionais agora. Suas razões técnicas, prós e contras foram documentados detalhadamente em [BACKEND_FUTURE_IMPROVEMENTS.md](file:///home/gabrieldnsilva/projects/LinkAuto-APP/docs/BACKEND_FUTURE_IMPROVEMENTS.md) para controle de backlog:

1. **Refresh token denylist (server-side)**: Adiada (YAGNI). O mecanismo local de rotação contínua atende perfeitamente à V1, postergando a necessidade do Redis para a V2 do sistema.
2. **Rate Limiting Distribuído**: Adiada (YAGNI). O rate limiting em memória do `slowapi` atende com folga ao perfil single-instance atual da V1.
3. **Escaneamento avançado/Antivírus em Uploads**: Adiada. A validação local por Magic Bytes determinística + MIME whitelist no upload de PDFs/imagens blinda o sistema contra invasões, dispensando infraestrutura pesada em lote.
4. **Fluxo completo de Password Reset com SES**: Adiada para a V2. O endpoint V1 retorna `202 Accepted` de forma auditável.
5. **HSTS e CSP completo**: Tratados diretamente no nível de infraestrutura de borda (Nginx/CloudFront).

---

## Ordem de Execução Recomendada

```
D02 (env.example) → D01 (admin block) → D03 (schema) → D05 (fail-fast)
→ D04 (headers) → D06 (magic bytes) → D11 (notification resilience)
→ D08 (SQL hardening) → D12 (N+1 fix) → D13 (scheduler resilience)
→ D07 (security logging) → D09 (rate limit) → D10 (abuse tests)
```

**Lógica**: P0 primeiro, depois P1 na ordem de menor risco de regressão,
depois P2 que podem depender dos anteriores (ex: testes de abuso testam rate limit).

---

## Referências

1. OWASP Top 10:2025 — https://owasp.org/Top10/2025/
2. OWASP API Security Top 10:2023 — https://owasp.org/API-Security/editions/2023/en/0x11-t10/
3. OWASP File Upload Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html
4. OWASP Logging Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html
5. slowapi docs — https://github.com/laurentS/slowapi
6. `docs/SECURITY_TECHNIQUES.md` — Auditoria interna do repositório
