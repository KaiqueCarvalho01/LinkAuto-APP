# 🔌 Backend Endpoint Requests — LinkAuto

Documento de especificações técnicas para solicitações de novos endpoints ou aprimoramentos no backend do LinkAuto, visando sustentar as melhorias recentes do frontend de forma integrada e otimizada.

---

## 1. Filtros Avançados na Busca de Instrutores [IMPLEMENTADO]

### Contexto
O frontend necessita refinar a listagem de instrutores geolocalizados por mais critérios profissionais, alinhando com a busca avançada.

### Especificação Entregue
Endpoint: `GET /api/v1/instructors/search` (com suporte a filtros e ordenação):
- **Especialidades:** `specialties` (filtro multi-valor case-insensitive).
- **Raio Máximo:** `radius_km` (calculado nativamente por fórmula de Haversine).
- **Ordenação:** `sort_by` (`rating`, `price_asc`, `price_desc`, `distance`).
- **Retorno:** Lista de instrutores contendo `slug` público para navegação anônima segura.

---

## 2. Endpoint de Contagem e Estatísticas Administrativas (Admin Dashboard) [IMPLEMENTADO]

### Contexto
Painel do administrador (`/admin/instructors`) exibindo métricas operacionais agregadas em tempo real.

### Especificação Entregue
Endpoint: `GET /api/v1/admin/stats` (restrito a role `ADMIN`):
```json
{
  "total_instructors": 3,
  "pending_instructors": 0,
  "approved_instructors": 3,
  "rejected_instructors": 0,
  "total_students": 1,
  "total_bookings": 2
}
```

---

## 3. Endpoint de Contagem e Estatísticas do Instrutor (Instructor Dashboard) [IMPLEMENTADO]

### Contexto
Painel do instrutor (`/instructor/dashboard`) exibindo agregação de horas, aulas e alunos atendidos.

### Especificação Entregue
Endpoint: `GET /api/v1/instructor/stats` (restrito a role `INSTRUTOR`):
```json
{
  "total_lessons": 2,
  "total_hours": 4,
  "unique_students": 1,
  "pending_bookings": 0
}
```

---

## 4. Endpoints Públicos de Perfil com Slugs Seguros (LGPD) [IMPLEMENTADO]

### Contexto
Permitir a navegação pública e anônima nos perfis de instrutores e alunos sem expor UUIDs internos, dados bancários, emails ou telefones antes da confirmação do agendamento.

### Especificação Entregue
- **Instrutor Público:** `GET /api/v1/instructors/{slug}/public`
  - Acesso público (anônimo).
  - Validação RN01: retorna 404 Not Found se o instrutor não estiver aprovado pelo Admin.
  - Oculta 100% de PII (email, telefone, CPF, documentos S3). Exibe bio, foto, especialidades, preço/hora, rating e reviews públicas.
- **Aluno Público:** `GET /api/v1/students/{slug}/public`
  - Acesso público.
  - Exibe resumo de reputação e contagem de aulas realizadas, sem expor penalidades ou contatos privados.

---

## 5. Jobs de Automação de Ciclo de Vida de Booking [IMPLEMENTADO]

### Contexto
Rotinas de cron disparadas para manutenção do estado de agendamentos e lembretes 24h.

### Especificação Entregue
- `POST /api/v1/jobs/booking-reminder` (envio de e-mails preventivos 24h antes da aula).
- `POST /api/v1/jobs/booking-timeout` (cancela reservas PENDENTES há mais de 24h).
- `POST /api/v1/jobs/booking-completion` (marca reservas CONFIRMADAS como REALIZADA 2h após término).
- **Contrato Unificado:** Retorno consistente com `processed`, `booking_ids`, `failed` e `failed_booking_ids`.
