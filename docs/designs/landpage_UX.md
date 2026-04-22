# UX.md — LinkAuto Landing Page (`/`)

> Documento base do frontend para planejamento com `speckit.plan` e `speckit.tasks`.
> Alinhado ao estado real do projeto em 2026-04-21.

---

## Objetivo

Definir o escopo ideal da landing em tarefas FE independentes, com dependencias explicitas,
para permitir planejamento e implementacao sem conflito com contrato backend, sem links quebrados
e sem dependencias de endpoints inexistentes.

---

## Baseline Tecnico Obrigatorio

- Router fonte de verdade: `src/app/router.tsx`
- Tema/tokens fonte de verdade: `src/theme/system.ts`
- Chakra UI: v3 (`@chakra-ui/react@3.x`)
  - Preferir API composta (`*.Root`, `*.Trigger`, `*.Content`, `*.Item`)
  - Preferir `colorPalette` (evitar exemplos legados com `colorScheme`)
- Sessao/autenticacao: `src/state/sessionStore.tsx`
- Mock atual de instrutores: `src/services/mockData.ts`
- Contrato de API: `specs/001-user-booking-domains/contracts/api-v1-openapi.yaml`

---

## Decisoes de Escopo Para Evitar Conflito com Backend

1. `/buscar` continua protegida por autenticacao (estado atual do router).
2. Nome canonico da rota administrativa: `/admin/instructors`.
3. Notificacoes na navbar autenticada entram com mock local nesta fase.
4. Hero com mapa integra com `GET /api/v1/instructors/search` quando disponivel e usa fallback local quando indisponivel.
5. Links de marketing sem rota atual entram via scaffold FE-008 antes da navbar final.

---

## Posicao no Processo SDD

```text
speckit.constitution
speckit.specify
speckit.plan
UX.md          <- este arquivo
speckit.tasks  <- gerar FE-001..FE-008 a partir daqui
```

---

## Estrutura Geral da Pagina

```text
NAVBAR (visitante/autenticado)
HERO (texto + mapa Leaflet)
SECAO como funciona
SECAO para alunos e instrutores
SECAO stats/destaques
TESTIMONIALS (alunos e instrutores)
FOOTER
```

---

## TASK-FE-001 — Navbar (Estado Visitante)

### FE-001 Arquivo e Dependencias

- Arquivo: `src/components/Navbar.tsx`
- Dependencia: FE-008

### FE-001 Especificacao

- Navbar fixa: `position="fixed"`, `top={0}`, `width="full"`, `zIndex={100}`, `h={16}`
- Ativar sombra quando `window.scrollY > 0`
- Logo com `RouterLink`
- Layout alvo:

```text
[Logo] [Explorar] [Para Alunos ▾] [Para Instrutores ▾] [Sobre] [Contato] [Entrar] [Comece agora]
```

- Menu desktop:

| Label | Destino | Estado esperado |
| ----- | ------- | --------------- |
| Explorar | `/` | Ja ativo |
| Para Alunos | dropdown | Scaffold FE-008 |
| Para Instrutores | dropdown | Scaffold FE-008 |
| Sobre | `/sobre` | Scaffold FE-008 |
| Contato | `/contato` | Scaffold FE-008 |

- Dropdown Para Alunos:
  - `/alunos/primeira-habilitacao`
  - `/alunos/habilitados`
  - `/alunos/como-funciona`
  - Ver Instrutores: visitante vai para `/login` e autenticado vai para `/buscar`
- Dropdown Para Instrutores:
  - `/cadastro?role=instrutor`
  - `/instrutores/como-funciona`
  - `/instrutores/vantagens`
  - `/instrutores/simulador`
- Botoes visitante:
  - Entrar -> `/login`
  - Comece agora -> `/cadastro`
- Mobile:
  - Ocultar menu desktop
  - Abrir drawer com mesmos links e CTAs

### FE-001 Criterio de Done

- [ ] Navbar sticky responsiva
- [ ] Dropdowns funcionam
- [ ] Nenhum link quebra (0 erro 404)
- [ ] Regra de auth de `/buscar` respeitada

---

## TASK-FE-002 — Navbar (Estado Autenticado)

### FE-002 Arquivo e Dependencias

- Arquivo: `src/components/Navbar.tsx` (extensao FE-001)
- Dependencia: FE-001

### FE-002 Especificacao

- Substituir CTAs de visitante por:

```text
[Notificacoes] [Avatar + Nome]
```

- Notificacoes:
  - `IconButton` com badge de nao lidas (`0` oculta badge)
  - `Popover` com ate 5 notificacoes
  - Link "Ver todas" para `/notificacoes`
  - Fonte de dados nesta fase: mock local (nao depender de endpoint backend)
- Avatar:
  - Exibir primeiro nome (ocultar em mobile)
  - Abrir sidebar de perfil (FE-003)

### FE-002 Criterio de Done

- [ ] Estado visitante oculto quando autenticado
- [ ] Badge some quando count = 0
- [ ] Popover fecha ao clicar fora
- [ ] Sidebar abre pela direita

---

## TASK-FE-003 — Sidebar de Perfil (Por Role)

### FE-003 Arquivo e Dependencias

- Arquivo: `src/components/ProfileSidebar.tsx`
- Dependencias: FE-001, FE-002

### FE-003 Especificacao

- Drawer lateral direita com overlay
- Cabecalho com avatar, nome, email e role ativa
- Para multi-role, usar tabs de role com API Chakra v3

- Rotas minimas alinhadas ao estado atual:

| Role | Item | Rota |
| ---- | ---- | ---- |
| ALUNO/INSTRUTOR | Minhas Aulas | `/agendamentos` |
| ALUNO/INSTRUTOR | Buscar Instrutor | `/buscar` |
| ALUNO/INSTRUTOR | Meu Perfil | `/profile` |
| ADMIN | Gerenciar Instrutores | `/admin/instructors` |
| ADMIN | Meu Perfil | `/profile` |

- Rotas futuras via scaffold FE-008:
  - `/aluno/mensagens`
  - `/instrutor/mensagens`
  - `/admin/audit`
  - `/ajuda`

- Logout:
  - Limpar sessao pelo provider atual
  - Redirecionar para `/login`

### FE-003 Criterio de Done

- [ ] Drawer abre/fecha corretamente
- [ ] Item ativo por rota atual
- [ ] Tabs so aparecem para multi-role
- [ ] Logout limpa sessao e redireciona

---

## TASK-FE-004 — Hero Section (Mapa Leaflet)

### FE-004 Arquivo e Dependencias

- Arquivo: `src/components/landing/HeroSection.tsx`
- Dependencia: FE-001

### FE-004 Especificacao

- Substitui o bloco visual estatico atual da Home
- Layout:
  - Desktop: texto (40%) + mapa (60%)
  - Mobile: texto acima e mapa abaixo

- CTAs:
  - Buscar Instrutores:
    - autenticado -> `/buscar`
    - visitante -> `/login`
  - Seja Instrutor -> `/cadastro?role=instrutor`

- Comportamento do mapa:
  - Solicitar geolocalizacao no mount
  - Sucesso: centralizar no usuario
  - Falha: fallback Mogi Mirim (`-22.4319`, `-46.9578`) com alerta
  - Renderizar marcadores com popup

- Integracao contratual:

```text
GET /api/v1/instructors/search
  ?lat={latitude}
  &lon={longitude}
  &radius=15
  &page=1
  &page_size=20
  [&specialties=...]
  [&min_rating=...]
  [&max_price=...]
```

- Fallback tecnico nesta fase:
  - fonte local: `src/services/mockData.ts` (`mockInstructors`)
  - nao usar caminhos inexistentes como `scripts/seed_demo.py` ou `src/mocks/instructors.ts`

### FE-004 Criterio de Done

- [ ] Geolocalizacao no load
- [ ] Fallback para Mogi Mirim + alerta
- [ ] Marcadores e popup funcionais
- [ ] Responsivo no mobile
- [ ] `leaflet/dist/leaflet.css` importado
- [ ] Fallback local ativo em erro de API

---

## TASK-FE-005 — Secoes Informativas

### FE-005 Arquivo e Dependencias

- Arquivo: `src/components/landing/InfoSections.tsx`
- Dependencia: FE-004

### FE-005 Especificacao

Blocos:

1. Como Funciona (3 passos)
2. Para Alunos / Para Instrutores
3. Stats/Numeros

Regras:

- Responsividade obrigatoria
- Icons Lucide
- Dados mockados permitidos nesta fase
- Conteudo que dependera de API deve conter marcador de integracao futura

### FE-005 Criterio de Done

- [ ] Secoes responsivas
- [ ] Sem acoplamento indevido com backend
- [ ] Estrutura semantica preservada

---

## TASK-FE-006 — Testimonials

### FE-006 Arquivo e Dependencias

- Arquivo: `src/components/landing/Testimonials.tsx`
- Dependencia: FE-005

### FE-006 Especificacao

- Duas visoes: Alunos e Instrutores
- Tabs com API Chakra v3 (`Tabs.Root`, `Tabs.List`, `Tabs.Trigger`, `Tabs.Content`)
- Grid responsivo em 1/2/3 colunas
- Cards com avatar, rating e texto

Dados:

- Fonte local dedicada (ex.: `src/services/mockTestimonials.ts`)
- Reutilizar `RatingStars` existente quando aplicavel

### FE-006 Criterio de Done

- [ ] Troca de abas funcional
- [ ] Grid responsivo
- [ ] Dados importados de arquivo local

---

## TASK-FE-007 — Footer

### FE-007 Arquivo e Dependencias

- Arquivo: `src/components/Footer.tsx`
- Dependencia: FE-008

### FE-007 Especificacao

- Background escuro com contraste AA
- Colunas de links para Alunos, Instrutores e institucional
- Linha inferior com copyright e redes
- Internos via `RouterLink`
- Externos via `Link` externo

### FE-007 Criterio de Done

- [ ] Contraste AA validado
- [ ] Links internos/externos corretos
- [ ] Responsivo no mobile

---

## TASK-FE-008 — Scaffold de Paginas e Rotas

### FE-008 Arquivo e Dependencias

- Arquivo principal: `src/app/router.tsx`
- Dependencia: nenhuma

### FE-008 Especificacao

Rotas scaffold obrigatorias:

- `/cadastro`
- `/sobre`
- `/contato`
- `/notificacoes`
- `/ajuda`
- `/admin/audit`
- `/alunos/primeira-habilitacao`
- `/alunos/habilitados`
- `/alunos/como-funciona`
- `/instrutores/como-funciona`
- `/instrutores/vantagens`
- `/instrutores/simulador`

Arquivos minimos:

```text
src/pages/Cadastro.tsx
src/pages/Sobre.tsx
src/pages/Contato.tsx
src/pages/Notificacoes.tsx
src/pages/Ajuda.tsx
src/pages/admin/AuditLog.tsx
src/pages/alunos/PrimeiraHabilitacao.tsx
src/pages/alunos/Habilitados.tsx
src/pages/alunos/ComoFunciona.tsx
src/pages/instrutores/ComoFunciona.tsx
src/pages/instrutores/Vantagens.tsx
src/pages/instrutores/Simulador.tsx
```

Regras:

- Registrar no router real (`src/app/router.tsx`)
- Manter imports relativos (evitar alias novo nesta fase)
- Boilerplate de pagina com titulo e placeholder

### FE-008 Criterio de Done

- [ ] Rotas registradas no router atual
- [ ] Sem erro 404 via navbar/footer
- [ ] Paginas scaffold renderizam corretamente

---

## Ordem de Execucao Recomendada

```text
FE-008 (Scaffold + Router)
    ↓
FE-001 (Navbar visitante)
    ↓
FE-007 (Footer)
    ↓
FE-002 (Navbar autenticado)
    ↓
FE-003 (Sidebar por role)
    ↓
FE-004 (Hero + mapa)
    ↓
FE-005 (Secoes informativas)
    ↓
FE-006 (Testimonials)
```

---

## Matriz de Dependencias de API

| Item FE | Endpoint | Status de contrato | Estrategia |
| ------- | -------- | ------------------ | ---------- |
| FE-004 mapa | `GET /api/v1/instructors/search` | Existe no OpenAPI | Usar contrato + fallback mock |
| FE-002 notificacoes | `GET /api/v1/notifications` | Nao consta no OpenAPI atual | Mock local ate definicao backend |
| FE-003 perfil/logout | `GET /users/me` e sessao atual | Existe e ja usado no frontend | Reutilizar SessionProvider |

---

## Checklist de Prontidao Para SpecKit

- [ ] IDs FE-001..FE-008 unicos e sem gaps
- [ ] Dependencias entre tasks explicitadas
- [ ] Rotas alvo alinhadas com `src/app/router.tsx`
- [ ] Politica de auth explicitada para `/buscar`
- [ ] Endpoints separados entre: contrato backend e mock local
- [ ] Uso de Chakra v3 documentado sem API legada
- [ ] Ordem de execucao definida para evitar retrabalho

---

*Ultima atualizacao: 2026-04-21 — LinkAuto v0.1 MVP Demo — Landing Page (Speckit-ready).*  
*Proximo UX.md sugerido: `/buscar` (filtros, mapa, lista e estado de loading/erro).*
