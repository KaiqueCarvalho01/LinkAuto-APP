# Checklist Curto — Prompt x UX x Codigo Atual (Landing)

Objetivo: validar rapidamente aderencia antes de implementar FE-001..FE-008.

Legenda de status:

- [x] alinhado
- [ ] pendente ou divergente
- [~] alinhado com ressalva

## Matriz Principal

| Item | Prompt (esperado) | UX revisado | Codigo atual | Status |
| ---- | ----------------- | ----------- | ------------ | ------ |
| Router de referencia | Usar router real do app | Aponta para src/app/router.tsx | Router ativo em src/app/router.tsx | [x] |
| Theme de referencia | Usar tema real do app | Aponta para src/theme/system.ts | Tema ativo em src/theme/system.ts | [x] |
| Chakra UI | Padrao v3 sem API legada | Exige v3 e evita exemplos legados | Projeto usa @chakra-ui/react 3.x | [x] |
| Politica de auth da busca | /buscar protegida para visitante | Documentada explicitamente | ProtectedRoute em /buscar | [x] |
| Navbar visitante | Links institucionais + dropdowns | Definida (FE-001) com dependencia FE-008 | Home atual ainda simplificada | [ ] |
| Navbar autenticada | Notificacoes + avatar + popover | Definida (FE-002) com mock local | Ainda nao implementada | [ ] |
| Sidebar por role | Drawer + itens por role + logout | Definida (FE-003) alinhada com rotas atuais | Ainda nao implementada | [ ] |
| Hero com mapa | Geolocalizacao + fallback Mogi Mirim | Definida (FE-004) com contrato + fallback | Home atual usa banner estatico | [ ] |
| Endpoint do mapa | GET /api/v1/instructors/search | Contrato documentado com query correta | OpenAPI contem endpoint | [x] |
| Fallback de mapa | Mock local sem caminho inexistente | Define src/services/mockData.ts | mockInstructors ja existe | [x] |
| Notificacoes backend | Endpoint pode nao existir agora | Define mock local nesta fase | Nao ha endpoint no contrato atual | [~] |
| Footer | Bloco global com contraste AA | Definido em FE-007 | Ainda nao implementado como componente global | [ ] |
| Testimonials | Bloco obrigatorio com tabs | Definido em FE-006 | Ainda nao implementado na home atual | [ ] |
| Scaffold de rotas | Criar paginas/rotas antes da navbar final | Definido em FE-008 | Rotas scaffold ainda nao criadas | [ ] |
| Naming admin | Padrao unico de rota admin | Usa /admin/instructors | Codigo atual usa /admin/instructors | [x] |

## Checklist de Go/No-Go para iniciar implementacao

- [x] UX aponta para arquivos reais do projeto
- [x] Regras de autenticacao estao explicitas no UX
- [x] Dependencias backend x mock local estao separadas
- [x] Ordem recomendada evita retrabalho (scaffold antes da navbar final)
- [ ] Rotas scaffold FE-008 criadas no router
- [ ] Componentes globais Navbar/Footer implementados
- [ ] Hero com mapa substituindo banner atual
- [ ] Testimonials implementado e integrado na landing

## Riscos de conflito com specs backend (se implementar fora da ordem)

- [ ] Implementar navbar final antes de FE-008 pode gerar links quebrados (404).
- [ ] Implementar notificacoes sem mock local pode travar por dependencia de endpoint nao contratado.
- [ ] Implementar mapa sem fallback pode quebrar UX em ambiente sem endpoint funcional.
- [ ] Alterar politica de /buscar para publico sem alinhamento pode divergir do fluxo de sessao atual.

## Decisao recomendada antes de codar

- [ ] Aprovar esta matriz.
- [ ] Iniciar FE-008 como etapa 1.
- [ ] Seguir sequencia FE-001 -> FE-007 -> FE-002 -> FE-003 -> FE-004 -> FE-005 -> FE-006.
