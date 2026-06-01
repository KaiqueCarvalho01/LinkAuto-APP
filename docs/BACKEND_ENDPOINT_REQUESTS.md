# 🔌 Backend Endpoint Requests — LinkAuto

Documento de especificações técnicas para solicitações de novos endpoints ou aprimoramentos no backend do LinkAuto, visando sustentar as melhorias recentes do frontend de forma integrada e otimizada.

---

## 1. Filtros Avançados na Busca de Instrutores

### Contexto
O frontend necessita refinar a listagem de instrutores geolocalizados por mais critérios profissionais, alinhando com a busca avançada.

### Recomendação
Estender o endpoint `GET /api/v1/instructors` (ou criar uma rota de busca dedicada) com suporte a query parameters adicionais:

- **Especialidades:** `specialties` (filtro por lista de strings, ex: `specialties=Baliza&specialties=Rodovias`).
- **Raio Máximo:** `radius_km` (filtro por distância limite de atendimento).
- **Ordenação:** `sort_by` (`rating`, `price_asc`, `price_desc`, `distance`).

---

## 2. Endpoint de Contagem e Estatísticas Administrativas (Admin Dashboard)

### Contexto
Atualmente, o painel do administrador (`/admin/instructors`) exibe apenas a lista de pendentes e faz aprovações. Para uma interface de governança completa e premium, necessitamos de métricas e contagens rápidas no dashboard.

### Recomendação
Criar um endpoint `GET /api/v1/admin/stats` (restrito a role `ADMIN`) que retorne:

```json
{
  "total_instructors": 18,
  "pending_instructors": 3,
  "approved_instructors": 12,
  "rejected_instructors": 3,
  "total_students": 145,
  "total_bookings": 412
}
```

---

## 3. Endpoint de Contagem e Estatísticas do Instrutor (Instructor Dashboard)

### Contexto
O painel do instrutor (`/instructor/dashboard`) precisa expor a contagem de aulas ministradas e horas dadas em tempo real de forma segura.

### Recomendação
Criar um endpoint `GET /api/v1/instructor/stats` (restrito a role `INSTRUTOR`) que retorne a agregação de dados do instrutor autenticado:

```json
{
  "total_lessons": 42,
  "total_hours": 84,
  "unique_students": 12,
  "pending_bookings": 2
}
```
