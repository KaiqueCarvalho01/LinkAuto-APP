![LinkAuto Logo](images/LinkAuto-logo-square.webp)

# LinkAuto - Tecnicas, Ferramentas e Seguranca

Este documento resume as tecnicas e ferramentas identificadas no scan geral do
repositorio `LinkAuto-APP`, com prioridade para `linkauto-backend` e apoio em
`linkauto-frontend`. A leitura foi orientada por OWASP Top 10:2025, OWASP API
Security Top 10:2023 e OWASP Cheat Sheet Series.

> [!IMPORTANT]
> Este arquivo nao substitui pentest, threat modeling formal ou revisao de
> infraestrutura em producao. Ele registra o estado observado no codigo e aponta
> prioridades praticas de hardening.

## 1. Escopo analisado

1. `linkauto-backend`
   - API Python com FastAPI.
   - Autenticacao, autorizacao, upload de documentos, validacao administrativa,
     notificacoes e regras iniciais de booking.
   - Testes de contrato e integracao com `pytest`.

2. `linkauto-frontend`
   - SPA React com Vite.
   - Rotas protegidas, cliente HTTP, sessao local e integracao com endpoints de
     auth/profile/admin.
   - Testes com Vitest, Testing Library e Playwright.

3. `infra`
   - Docker Compose local para backend e frontend.
   - Uso de `.env.example` como fonte de variaveis no ambiente de dev.

## 2. Ferramentas e tecnologias identificadas

1. Backend
   - Python 3.11.
   - FastAPI para API HTTP e OpenAPI.
   - Pydantic e Pydantic Settings para schemas e configuracao.
   - SQLAlchemy 2 e Alembic para modelagem/migracoes.
   - SQLite em desenvolvimento.
   - PostgreSQL + PostGIS como alvo de producao descrito nas specs.
   - `bcrypt` para hashing de senhas.
   - `python-jose[cryptography]` para JWT.
   - `python-multipart` para upload.
   - `boto3` para AWS SES/S3.
   - Uvicorn como servidor ASGI.

2. Frontend
   - React 19.
   - Vite.
   - TypeScript.
   - React Router DOM.
   - Chakra UI.
   - Tailwind CSS 4.
   - Leaflet/React Leaflet.
   - Lucide React.

3. Qualidade e testes
   - `pytest` e `pytest-asyncio`.
   - `httpx`/FastAPI TestClient nos testes.
   - Ruff para lint do backend.
   - ESLint e TypeScript no frontend.
   - Vitest, Testing Library e Playwright.

4. Integracoes e operacao
   - AWS SES para notificacoes.
   - AWS S3 previsto para documentos.
   - Docker Compose para ambiente local.
   - Contrato OpenAPI em `specs/001-user-booking-domains/contracts/api-v1-openapi.yaml`.

## 3. Tecnicas de seguranca ja aplicadas

1. Hash de senha com algoritmo dedicado
   - Senhas sao armazenadas com `bcrypt`, nao em texto puro.
   - Local: `linkauto-backend/app/core/security.py`.
   - OWASP relacionado: A04 Cryptographic Failures e A07 Authentication Failures.

2. Modelo de access token + refresh token
   - Access token JWT com expiracao curta configuravel.
   - Refresh token separado, com tipo proprio no payload.
   - Local: `linkauto-backend/app/core/security.py`.

3. Refresh token em cookie com flags de seguranca
   - Cookie `refresh_token` usa `HttpOnly`, `Secure` e `SameSite=Strict`.
   - Path restrito para `/api/v1/auth/refresh`.
   - Local: `linkauto-backend/app/api/v1/auth.py`.

4. Bearer token para endpoints protegidos
   - Dependencia centralizada valida o token e exige tipo `access`.
   - Local: `linkauto-backend/app/api/deps/authn.py`.

5. RBAC por papeis
   - Controle de acesso baseado em `ALUNO`, `INSTRUTOR` e `ADMIN`.
   - Endpoints administrativos exigem papel `ADMIN`.
   - Local: `linkauto-backend/app/api/deps/authz.py`.

6. Controle de propriedade em upload de documentos
   - Instrutor so pode enviar documentos para si mesmo; admin pode enviar para
     outro instrutor.
   - Local: `linkauto-backend/app/api/v1/instructor_documents.py`.

7. Validacao de upload
   - Whitelist de MIME types: PDF, JPEG e PNG.
   - Limite maximo de 10 MB por arquivo.
   - Sanitizacao basica de nome com `Path(filename).name`.
   - Local: `linkauto-backend/app/services/instructor_document_service.py`.

8. Reducao de exposicao publica de instrutores
   - Lista publica retorna apenas instrutores aprovados e ativos.
   - Local: `linkauto-backend/app/services/profile_service.py`.

9. Fluxo administrativo de credenciamento
   - Admin aprova/rejeita instrutores.
   - O estado DETRAN separa `PENDENTE`, `APROVADO` e `REJEITADO`.
   - Local: `linkauto-backend/app/services/admin_validation_service.py`.

10. Retencao minima de documentos sensiveis
    - Apos decisao administrativa, documentos sao purgados do store atual.
    - A intencao de S3 purge esta documentada nas specs.
    - Local: `linkauto-backend/app/services/document_cleanup_service.py`.

11. CORS configuravel
    - Origins permitidas vem de `CORS_ORIGINS`, evitando wildcard fixo no codigo.
    - Local: `linkauto-backend/app/core/config.py`.

12. Envelopes padronizados de resposta
    - Respostas de sucesso e erro seguem formato consistente.
    - Ajuda clientes a tratar erros sem depender de mensagens soltas.
    - Local: `linkauto-backend/app/schemas/common.py`.

13. Tratamento global de erro HTTP e validacao
    - `HTTPException` e `RequestValidationError` retornam envelope padronizado.
    - Local: `linkauto-backend/app/main.py`.

14. Validacao de paginacao administrativa
    - `page` e `page_size` usam restricoes `ge=1` e `le=100`.
    - Reduz risco de consumo excessivo em listagens.
    - Local: `linkauto-backend/app/api/v1/admin_instructors.py`.

15. Estado de booking como maquina de estados
    - Transicoes permitidas sao declaradas em um mapa explicito.
    - Transicoes invalidas disparam erro de dominio.
    - Local: `linkauto-backend/app/domain/booking.py`.

16. Reserva atomica de slots
    - O servico reserva slots apenas se todos estiverem disponiveis.
    - Implementacao SQL usa parametros vinculados para `slot_ids` e status.
    - Local: `linkauto-backend/app/services/booking_lock_service.py`.

17. Testes de seguranca funcional
    - Cobertura atual valida cookie seguro, endpoint protegido sem token, RBAC
      indireto, upload invalido, limite de arquivo e visibilidade publica.
    - Locais: `linkauto-backend/tests/contract` e `linkauto-backend/tests/integration`.

18. Cliente HTTP com credenciais explicitas
    - Frontend envia cookies com `credentials: "include"` e bearer token quando
      disponivel.
    - Local: `linkauto-frontend/src/services/httpClient.ts`.

19. Rotas protegidas no frontend
    - `ProtectedRoute` bloqueia usuarios nao autenticados.
    - `RoleRoute` aplica restricoes por papel para telas especificas.
    - Local: `linkauto-frontend/src/app/router.tsx`.

20. Governanca de iteracoes no frontend
    - Existem regras/testes de boundary, endpoint policy, coverage policy e
      quality gate.
    - Local: `linkauto-frontend/src/features/iteration-governance`.

## 4. Mapeamento OWASP Top 10:2025

| Categoria OWASP | Evidencias no LinkAuto | Estado |
| --- | --- | --- |
| A01 Broken Access Control | RBAC, endpoints protegidos, visibilidade publica apenas para instrutor aprovado | Parcial |
| A02 Security Misconfiguration | CORS configuravel, env settings, Docker local | Requer hardening |
| A03 Software Supply Chain Failures | `pyproject.toml`, `package-lock.json`, testes e lint | Requer SCA automatizado |
| A04 Cryptographic Failures | bcrypt, JWT, cookie seguro para refresh | Parcial |
| A05 Injection | Pydantic/FastAPI, SQLAlchemy, parametros vinculados em slots | Parcial |
| A06 Insecure Design | State machine de booking, lifecycle de documentos, specs | Parcial |
| A07 Authentication Failures | login, refresh, hash de senha, token typado | Parcial |
| A08 Software or Data Integrity Failures | Contratos, testes, migrations, lockfile frontend | Requer CI e assinatura/controle de supply chain |
| A09 Security Logging and Alerting Failures | Catalogo de notificacoes existe | Lacuna relevante |
| A10 Mishandling of Exceptional Conditions | Envelopes de erro e handlers globais | Parcial |

## 5. Riscos prioritarios encontrados

1. Registro permite solicitar papel `ADMIN`
   - Severidade: critica.
   - Evidencia: `RegisterRequest.roles` recebe lista enviada pelo cliente e
     `IdentityStore.create_user` aceita qualquer role valida, incluindo `ADMIN`.
   - Impacto: um usuario externo pode criar conta administrativa se o endpoint
     estiver exposto.
   - Recomendacao: bloquear `ADMIN` no registro publico; criar admins por seed,
     console administrativo seguro ou fluxo interno auditado.
   - OWASP: A01 Broken Access Control, A07 Authentication Failures.

2. Segredos reais ou realistas em `.env.example`
   - Severidade: critica.
   - Evidencia: `linkauto-backend/.env.example` contem valores preenchidos para
     AWS access key, AWS secret key, bucket, e-mail e JWT secret.
   - Impacto: vazamento de credenciais, uso indevido de SES/S3, takeover de
     tokens se o secret for usado fora de dev.
   - Recomendacao: rotacionar imediatamente as credenciais, substituir por
     placeholders e habilitar secret scanning no repositorio.
   - OWASP: A02 Security Misconfiguration, A03 Software Supply Chain Failures.

3. Access token persistido em `localStorage`
   - Severidade: alta.
   - Evidencia: `linkauto-frontend/src/state/sessionStore.tsx` persiste
     `accessToken` em `localStorage`.
   - Impacto: XSS pode extrair token de acesso.
   - Recomendacao: preferir access token em memoria, renovacao por refresh cookie
     `HttpOnly` e CSP forte.
   - OWASP: A07 Authentication Failures.

4. Ausencia de rate limiting e protecao anti-abuso
   - Severidade: alta.
   - Evidencia: nao foi identificado middleware de rate limit em login, register,
     refresh, password-reset ou upload.
   - Impacto: brute force, credential stuffing, spam de reset e DoS por upload.
   - Recomendacao: aplicar rate limit por IP/conta/rota, lockout progressivo e
     monitoramento de tentativas.
   - OWASP: A07 Authentication Failures, API4 Unrestricted Resource Consumption.

5. Upload valida MIME declarado, mas nao conteudo real
   - Severidade: alta.
   - Evidencia: validacao usa `UploadFile.content_type`.
   - Impacto: arquivo malicioso pode declarar MIME permitido.
   - Recomendacao: validar magic bytes, extensao, antivirus/sandbox, storage
     privado, nomes nao previsiveis e assinatura temporaria para acesso.
   - OWASP: A05 Injection, A10 Mishandling of Exceptional Conditions.

6. Perfil aceita campos extras livremente
   - Severidade: media/alta.
   - Evidencia: `UserMePatchRequest` usa `extra="allow"` e repassa payload para
     atualizacao.
   - Impacto: risco de mass assignment em evolucoes futuras.
   - Recomendacao: schemas fechados por perfil e allowlist por campo.
   - OWASP: A01 Broken Access Control, API3 Broken Object Property Level Authorization.

7. Refresh token nao tem revogacao server-side
   - Severidade: media/alta.
   - Evidencia: token tem `jti`, mas nao foi identificado denylist/store de
     revogacao ou reutilizacao.
   - Impacto: token furtado permanece valido ate expiracao.
   - Recomendacao: registrar `jti`, rotacionar com invalidacao do anterior,
     detectar reuse e revogar sessoes.
   - OWASP: A07 Authentication Failures.

8. Logging e alerting de seguranca ainda ausentes
   - Severidade: media/alta.
   - Evidencia: nao foi identificado logger estruturado para auth failures,
     forbidden, uploads rejeitados, decisao admin e excecoes de integracao.
   - Impacto: incidentes ficam sem trilha operacional adequada.
   - Recomendacao: incluir logs estruturados sem segredos/PII sensivel e alertas
     para eventos de auth, admin, upload e integracoes.
   - OWASP: A09 Security Logging and Alerting Failures.

9. Politicas de headers HTTP nao aparecem no app
   - Severidade: media.
   - Evidencia: nao foi identificado middleware para HSTS, CSP, X-Content-Type-
     Options, Referrer-Policy e Permissions-Policy.
   - Impacto: maior exposicao a XSS, clickjacking e misconfiguration.
   - Recomendacao: aplicar headers no reverse proxy e/ou middleware ASGI.
   - OWASP: A02 Security Misconfiguration.

10. CORS permite credenciais
    - Severidade: media.
    - Evidencia: `allow_credentials=True`.
    - Impacto: exige controle rigoroso de origins por ambiente.
    - Recomendacao: manter allowlist estrita por ambiente; evitar regex ampla;
      auditar preview/staging domains.
    - OWASP: A02 Security Misconfiguration.

11. SQL bruto com table name interpolado
    - Severidade: media.
    - Evidencia: `SqlAlchemySlotReservationStore` usa f-string para
      `table_name`.
    - Impacto: hoje o valor padrao e interno, mas vira risco se algum dia for
      configuravel por entrada externa.
    - Recomendacao: manter `table_name` constante ou validar contra allowlist.
    - OWASP: A05 Injection.

12. Password reset ainda e placeholder
    - Severidade: media.
    - Evidencia: `trigger_password_reset` retorna sem gerar token, expiracao ou
      fluxo de confirmacao.
    - Impacto: funcionalidade incompleta pode ser mal interpretada como pronta.
    - Recomendacao: implementar token de uso unico, expiracao curta, generic
      response, rate limit e logs.
    - OWASP: A07 Authentication Failures.

## 6. Recomendacoes de hardening por prioridade

1. P0 - Corrigir controle de criacao de admins
   - Remover `ADMIN` do registro publico.
   - Criar rota/seed administrativa fora do fluxo publico.
   - Adicionar teste provando que registro publico com `ADMIN` retorna 400/403.

2. P0 - Remover e rotacionar segredos
   - Trocar todos os valores sensiveis expostos em `.env.example`.
   - Revogar/rotacionar chaves AWS e JWT secret.
   - Adicionar `.env.example` apenas com placeholders.
   - Habilitar secret scanning no GitHub.

3. P1 - Fortalecer sessao
   - Manter access token apenas em memoria no frontend.
   - Usar refresh cookie `HttpOnly` para renovacao.
   - Armazenar e invalidar `jti` de refresh token.
   - Implementar logout server-side.

4. P1 - Adicionar rate limiting
   - Aplicar limites em `/auth/login`, `/auth/register`, `/auth/refresh`,
     `/auth/password-reset` e uploads.
   - Diferenciar limites por IP, usuario e rota.

5. P1 - Fechar schemas de entrada
   - Substituir `extra="allow"` por schemas explicitos.
   - Usar allowlist por perfil e por papel.
   - Bloquear campos sensiveis em updates de usuario.

6. P1 - Elevar validacao de upload
   - Validar magic bytes.
   - Gerar object keys com UUID, sem nome original como chave principal.
   - Fazer scan antivirus/antimalware.
   - Usar bucket privado e URLs assinadas com expiracao.

7. P2 - Adicionar logging de seguranca
   - Registrar login success/failure, refresh failure, forbidden, upload
     rejection, admin approval/rejection e excecoes de integracao.
   - Mascarar tokens, passwords, connection strings, chaves e PII sensivel.

8. P2 - Adicionar security headers
   - CSP, HSTS, X-Content-Type-Options, Referrer-Policy, Permissions-Policy.
   - Definir tambem no reverse proxy/CDN quando existir.

9. P2 - Automatizar supply chain security
   - `pip-audit` ou equivalente para Python.
   - `npm audit`/Dependabot para Node.
   - CI com lint, testes, SCA e secret scanning.

10. P2 - Definir politica LGPD operacional
    - Retencao minima de documentos.
    - Base legal e finalidade.
    - Auditoria de acesso administrativo.
    - Processo de exclusao/anonimizacao.

## 7. Tecnicas recomendadas para evolucao do backend

1. Threat modeling por fluxo
   - Autenticacao.
   - Credenciamento de instrutor.
   - Upload/consulta de documentos.
   - Booking e pagamentos futuros.
   - Mensagens e reviews.

2. Defense in depth
   - Validacao de entrada no schema.
   - Autorizacao no service layer.
   - Constraints no banco.
   - Logs e alertas operacionais.

3. Zero trust para integracoes
   - Timeouts e retries com limite para SES/S3.
   - Tratamento de erro sem vazar detalhes.
   - Permissoes IAM minimas por servico.

4. Secure-by-default config
   - Falhar startup em producao se `JWT_SECRET=change-me`.
   - Exigir `APP_ENV=production` com `RESET_SQLITE_ON_STARTUP=false`.
   - Bloquear CORS vazio/amplo em producao.

5. Testes orientados a abuso
   - Usuario comum tentando endpoint admin.
   - Usuario tentando alterar role.
   - Upload com MIME falso.
   - Refresh token reutilizado.
   - Login brute force.
   - Payload com campos extras.

## 8. Checklist rapido por release

1. Antes de subir backend
   - `ruff check .`
   - `pytest`
   - Verificar se `.env` real nao foi versionado.
   - Verificar se `.env.example` contem apenas placeholders.
   - Rodar SCA em dependencias Python.

2. Antes de subir frontend
   - `npm run lint`
   - `npm run typecheck`
   - `npm run build`
   - `npm run test`
   - Rodar SCA em dependencias Node.

3. Antes de expor ambiente publico
   - HTTPS obrigatorio.
   - Headers de seguranca configurados.
   - CORS restrito.
   - Rate limit ativo.
   - Logs de auth/admin/upload ativos.
   - Credenciais AWS rotacionadas e com IAM minimo.

## 9. Referencias usadas

1. OWASP Top 10:2025
   - https://owasp.org/Top10/2025/

2. OWASP Top 10 official repository
   - https://github.com/OWASP/Top10

3. OWASP API Security Top 10:2023
   - https://owasp.org/API-Security/editions/2023/en/0x11-t10/

4. OWASP Authentication Cheat Sheet
   - https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html

5. OWASP Session Management Cheat Sheet
   - https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html

6. OWASP Logging Cheat Sheet
   - https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html

7. OWASP Cheat Sheet Series
   - https://cheatsheetseries.owasp.org/
