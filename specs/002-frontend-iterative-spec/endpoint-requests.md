# Endpoint Requests - Frontend Brownfield Governance

Objetivo: registrar, antes de implementar, qualquer necessidade de novo endpoint para suportar evolucao do frontend sem quebrar contratos backend.

## Regras

- Toda necessidade de endpoint novo deve ser registrada aqui antes de iniciar implementacao backend relacionada.
- Toda entrada deve conter justificativa funcional e tecnica.
- Sempre avaliar alternativa de mock/fallback antes de propor endpoint novo.
- Quando aprovado, referenciar o contrato/backend spec correspondente.

## Template de registro

```md
## ER-XXX - [titulo curto]

- Data:
- Solicitante:
- Iteracao frontend:
- User Story/feature relacionada:

### Contexto
[qual problema de produto/ux precisa ser resolvido]

### Contrato atual
[quais endpoints existem hoje e por que nao atendem]

### Proposta de endpoint
- Metodo:
- Path:
- Parametros:
- Resposta esperada:

### Alternativas avaliadas
- Mock local:
- Reuso de endpoint existente:
- Ajuste de UX sem endpoint novo:

### Justificativa
[por que endpoint novo e necessario agora]

### Impacto
- Frontend:
- Backend:
- Testes:
- Risco tecnico:

### Decisao
- Status: Proposto | Em analise | Aprovado | Rejeitado | Postergado
- Responsavel:
- Referencias:
```

## Registros

Nenhum endpoint novo solicitado ate o momento.

### Exemplo de ciclo de vida (Referencia)

```md
## ER-000 - Exemplo de Endpoint Request
- Data: 2026-04-22
- Solicitante: Dev frontend
- Iteracao frontend: 001
- Status: APPROVED
- Justificativa: Necessario criar recurso porque os slots locais precisam sincronizar com o banco.
- Impacto: Baixo. Endpoint isolado.
- Referencias: specs/001-user-booking-domains/...
```
