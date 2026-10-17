# Decisões e Checklist de Rollout

Este documento registra decisões tomadas durante o desenvolvimento, para que possam ser revisitadas, e o que ainda precisa ser feito **fora do código** (configurações do GitHub e da infraestrutura) para colocar o LinkAuto em produção. Ele substitui a issue #57 como fonte de verdade: atualize-o no mesmo PR que mudar uma destas decisões.

---

## 1. Decisões

### Pilha #34–#48

| Decisão | Motivo / custo | Origem |
| :--- | :--- | :--- |
| As respostas de agendamento trazem o resumo público do instrutor (`slug`, nome, avatar, cidade/UF); a lista pública não expõe UUIDs. | O frontend não precisa cruzar UUIDs com a lista pública. | #44 |
| Os papéis (roles) são lidos do banco a cada requisição, não do JWT. | Uma consulta por chave primária por requisição; remover um papel ou desativar a conta vale na hora. | #42 |
| Logout revoga a sessão inteira (família de refresh tokens), não só o token apresentado. | Outros dispositivos continuam logados. | #43 |
| Limite de login por conta: 10 tentativas a cada 15 minutos por e-mail, além de 10/min por IP. | Proteção contra força bruta, com o risco de alguém bloquear um e-mail conhecido por 15 minutos. Pode virar atraso progressivo se os bloqueios gerarem suporte. | #47 |
| **Redis é opcional.** Sem `RATE_LIMIT_STORAGE_URI=redis://...`, os limites são contados por processo e produção registra um aviso. Fora de `development`/`test`/`ci` (qualquer outro `APP_ENV`, não só `production`, #79), a API não inicia com `JWT_SECRET` inseguro ou `RESET_SQLITE_ON_STARTUP`. | Decisão do time. | #47, #79 |
| **S3 é opcional.** Sem `S3_BUCKET`, documentos de instrutores ficam no disco local em `DOCUMENT_STORAGE_PATH` (volume `/app/storage` na imagem de produção), com links assinados (HMAC) de 5 minutos para admins. | Decisão do time. | #46 |
| **E-mail é opcional** (ainda não há provedor). Sem `SES_FROM_EMAIL`, as notificações são ignoradas e registradas em log (INFO) em todos os ambientes; `EMAIL_BACKEND=disabled` desliga explicitamente. | Decisão do time. Toda funcionalidade precisa funcionar sem e-mail. | #45 |
| O desenvolvimento continua usando `create_all` + seed em vez de migrações. | Fica para o time decidir. | #39, #28 |

### Pilha #50–#57

| Decisão | Motivo / custo | Origem |
| :--- | :--- | :--- |
| As rotas recebem o `NotificationService` por injeção de dependência (`Notifications`). | Todas as rotas que notificam ficam ligadas da mesma forma, e os testes conseguem capturar os e-mails. | #50 |
| Quem cancela um agendamento é definido pelo próprio agendamento (aluno ou instrutor dele), não pelos papéis do usuário. `GET /bookings?as=student\|instructor`; sem `as`, usuários com os dois papéis veem os dois lados. Ninguém agenda os próprios horários. | Usuários com ALUNO e INSTRUTOR não conseguiam ver nem cancelar as aulas que marcaram. | #51 |
| Os textos dos e-mails ficam em `notification_templates.py`; cada destinatário recebe o seu e-mail, com nomes (ou "Aluno"/"Instrutor"), data/horário da aula e link para o app (`FRONTEND_URL`). IDs internos nunca aparecem. Notificações para a administração vão para `ADMIN_NOTIFICATION_EMAIL` (ignoradas se ausente). | Os e-mails mostravam UUIDs. | #55 |
| O painel do instrutor lista as solicitações pendentes (`GET /bookings?status=PENDENTE&as=instructor`) para confirmar ou recusar; o agendamento traz o nome do aluno. | Os e-mails pediam ao instrutor que respondesse no painel, que não mostrava nada. | #55 |
| O horário da aula nos e-mails usa o relógio UTC armazenado, como o frontend (`getUTCHours`). | Mantém e-mail e app consistentes. Se o app passar a converter para o fuso de Brasília, ajuste `format_lesson_time` junto. | #55 |
| Redefinição de senha com link de uso único (hash SHA-256 no banco; 30 min por e-mail; limite de 3 pedidos por hora por e-mail). **Sem e-mail**, o pedido público não gera link; um admin confirma a identidade por outro canal e gera o link (`POST /admin/users/{id}/password-reset-link`, 24 h). Pedidos públicos nunca invalidam um link de admin, e contas de admin não recebem links por essa rota. Em `development` o link também vai para o log. Redefinir a senha desconecta todas as sessões. | O pedido de redefinição não fazia nada, e não há provedor de e-mail. | #52 |
| Os jobs rodam por CLI (`python -m app.jobs run all`), agendados **uma vez por ambiente** a cada 15 minutos. Rodar duas vezes, inclusive em paralelo, é seguro (`UPDATE` condicional por agendamento). O timeout libera os horários e avisa os dois lados. Os e-mails saem antes do commit da execução: se o commit falhar, a próxima execução pode repetir um e-mail (entrega pelo menos uma vez). | Sem agendamento, solicitações nunca expiravam, aulas nunca viravam `REALIZADA` (bloqueando avaliações) e lembretes nunca saíam. | #53 |
| O job `token-cleanup` apaga refresh tokens e links de redefinição vencidos há mais de 1 dia. | A tabela `refresh_tokens` crescia sem limite; a folga mantém a detecção de reuso. | #54 |

---

## 2. Checklist de Rollout

### GitHub (requer permissão de admin no repositório)
- [ ] Tornar **Backend OK** e **Frontend OK** status checks obrigatórios em `main` (Settings → Branches).

### Produção
- [ ] Rodar `scripts/migrate.sh` como passo de pré-deploy no pipeline (ver [`infra/README.md`](../infra/README.md#-migrações-no-deploy-produção)). Esta pilha adiciona a migração `0004` (`password_reset_tokens`).
- [ ] Agendar `python -m app.jobs run all` a cada 15 minutos, **uma vez por ambiente** (ex.: `CronJob` do Kubernetes com `concurrencyPolicy: Forbid`). Ver [`infra/README.md`](../infra/README.md#-jobs-agendados-agendamentos).
- [ ] Montar um volume persistente em `/app/storage` (documentos de instrutores).
- [ ] Definir `PUBLIC_API_URL`, `FRONTEND_URL` (links nos e-mails e na redefinição de senha) e, atrás de proxy reverso, `TRUSTED_PROXIES`.
- [ ] Combinar com a equipe de suporte o procedimento para gerar links de redefinição de senha enquanto não houver e-mail (confirmar a identidade antes).

### Opcional / mais tarde
- [ ] Com várias réplicas ou workers: adicionar Redis e definir `RATE_LIMIT_STORAGE_URI`.
- [ ] Mover documentos para um bucket S3 privado (Block Public Access ligado; IAM em `instructors/*` limitado a `s3:PutObject`, `s3:GetObject` e `s3:DeleteObject`) definindo `S3_BUCKET`.
- [ ] Quando houver provedor de e-mail: verificar o remetente no SES e definir `SES_FROM_EMAIL`; definir `ADMIN_NOTIFICATION_EMAIL`.
- [ ] Acompanhar a correção do slowapi para Python 3.16 ([laurentS/slowapi#263](https://github.com/laurentS/slowapi/issues/263)); o aviso está filtrado em `pyproject.toml`.
