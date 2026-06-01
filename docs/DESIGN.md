# DESIGN.md — LinkAuto

> Design system reference para o frontend do LinkAuto.
> Stack: React 19 + Vite + Tailwind CSS 4 + Chakra UI v3 + Leaflet + Zustand + Vitest
> Consumido pelo agente Gemini e engenheiros do LinkAuto.

---

## 1. Brand Identity

### Conceito Visual

O LinkAuto une dois mundos: **conexão humana** (Link) e **mobilidade urbana** (Auto).
O símbolo entrelaça as letras L e A em torno de um volante estilizado com um pino de localização no centro — reforçando a busca geolocalizada como diferencial do produto.

O tom visual é **confiante e técnico, mas acessível**: não é uma fintech fria nem um app de delivery casual. É uma plataforma profissional para um serviço regulamentado.

### Direção Estética

**Refined Civic Tech** — limpa, estruturada, mobile-first. Usa a paleta verde/azul da logo com generoso espaço em branco, tipografia sem serifa de peso variável e elementos de mapa como textura de contexto. Não é flat puro nem glassmorphism — é **substance over style**.

---

## 2. Paleta de Cores

Extraída da logo gerada (arquivo `LinkAuto-banner.webp`).

### Tokens Primários

| Token | Hex | Uso |
|---|---|---|
| `--la-blue` | `#1A6DB5` | "Link" na logo · Ações primárias · Links |
| `--la-green` | `#3EAA5B` | "Auto" na logo · Sucesso · Badge de credenciado |
| `--la-blue-dark` | `#124E87` | Hover de botões primários · Cabeçalhos |
| `--la-green-dark` | `#2C7D42` | Hover de elementos verdes · Status aprovado |
| `--la-blue-light` | `#D6E8F7` | Backgrounds sutis de info · Chips de filtro |
| `--la-green-light` | `#D4EFE0` | Backgrounds de sucesso · Badge aprovado bg |

### Tokens Neutros

| Token | Hex | Uso |
|---|---|---|
| `--la-gray-900` | `#111827` | Texto principal |
| `--la-gray-700` | `#374151` | Texto secundário |
| `--la-gray-500` | `#6B7280` | Subtítulos · Placeholders · Labels |
| `--la-gray-300` | `#D1D5DB` | Bordas · Dividers |
| `--la-gray-100` | `#F3F4F6` | Backgrounds de cards · Input fill |
| `--la-white` | `#FFFFFF` | Surface principal |

### Tokens Semânticos

| Token | Valor | Uso |
|---|---|---|
| `--la-pending` | `#F59E0B` | Status PENDENTE |
| `--la-confirmed` | `#1A6DB5` | Status CONFIRMADA |
| `--la-completed` | `#3EAA5B` | Status REALIZADA |
| `--la-cancelled` | `#EF4444` | Status CANCELADA |
| `--la-blocked` | `#9CA3AF` | Slot BLOQUEADO · Usuário penalizado |

### Modo Escuro e Contraste Operacional

Para garantir legibilidade consistente em todas as telas, o frontend passou a usar tokens semanticos Chakra como fonte primaria de cor para texto, superfícies, bordas e feedback visual.

Tokens semanticos adotados como base em componentes e páginas:

- `surface.canvas`, `surface.panel`, `surface.muted`
- `text.primary`, `text.secondary`, `text.muted`, `text.inverse`
- `border.default`, `border.subtle`
- `brand.solid`, `brand.emphasized`, `brand.muted`
- `accent.solid`, `accent.emphasized`, `accent.muted`
- `state.warning.*`, `state.success.*`, `state.danger.*`

Regras obrigatorias:

- Evitar hardcode de tons neutros (`white`, `#111827`, `#D1D5DB`, etc.) em elementos Chakra de UI.
- Priorizar tokens semanticos para textos e fundos em vez de escalas fixas de cinza.
- Preservar apenas excecoes tecnicas onde o container visual e externo ao sistema de temas (ex.: popup nativo do Leaflet).

Comportamento de troca de tema:

- O modo claro/escuro e alternado por controle global na UI.
- A preferencia do usuario e persistida em `localStorage` com a chave `linkauto-color-mode`.
- O tema escuro e aplicado via classe raiz `.dark`, em conformidade com o seletor de dark mode do Chakra v3.

### Configuração Tailwind CSS 4

Em `tailwind.config.ts` ou no arquivo CSS global com `@theme`:

```css
@import "tailwindcss";

@theme {
  --color-la-blue: #1A6DB5;
  --color-la-blue-dark: #124E87;
  --color-la-blue-light: #D6E8F7;
  --color-la-green: #3EAA5B;
  --color-la-green-dark: #2C7D42;
  --color-la-green-light: #D4EFE0;

  --color-la-pending: #F59E0B;
  --color-la-confirmed: #1A6DB5;
  --color-la-completed: #3EAA5B;
  --color-la-cancelled: #EF4444;
  --color-la-blocked: #9CA3AF;
}
```

---

## 3. Tipografia

### Fontes

| Papel | Fonte | Weights | Import |
|---|---|---|---|
| Display / Headings | **DM Sans** | 500, 700 | Google Fonts |
| Body / UI | **DM Sans** | 400, 500 | Google Fonts |
| Monospace (código/ids) | **JetBrains Mono** | 400 | Google Fonts |

> Justificativa: DM Sans é geométrica mas com personalidade — evita o clichê Inter/Roboto. Tem excelente legibilidade em mobile e suporta acentuação PT-BR sem fallback.

### Escala Tipográfica

```css
/* Tailwind CSS 4 custom font sizes via @theme */
@theme {
  --font-family-sans: 'DM Sans', sans-serif;
  --font-family-mono: 'JetBrains Mono', monospace;

  /* Escala */
  --font-size-xs:   0.75rem;   /* 12px — Labels, badges */
  --font-size-sm:   0.875rem;  /* 14px — Corpo secundário, captions */
  --font-size-base: 1rem;      /* 16px — Corpo principal */
  --font-size-lg:   1.125rem;  /* 18px — Subtítulos de card */
  --font-size-xl:   1.25rem;   /* 20px — Títulos de seção mobile */
  --font-size-2xl:  1.5rem;    /* 24px — Títulos de página */
  --font-size-3xl:  1.875rem;  /* 30px — Hero headings */
}
```

### Regras de Uso

- **Peso 700** somente para headings de página (h1/h2) e CTAs.
- **Peso 500** para labels de formulário, nomes de instrutores, títulos de card.
- **Peso 400** para corpo de texto, descrições, mensagens.
- Nunca usar tamanho abaixo de `sm` em elementos interativos (acessibilidade touch).
- Linha (`leading`) padrão: `1.6` para corpo; `1.2` para headings grandes.

---

## 4. Espaçamento e Layout

### Grid

- **Mobile (< 640px):** 1 coluna, padding horizontal `px-4` (16px)
- **sm (640px+):** 2 colunas para cards de instrutores
- **md (768px+):** Sidebar + content em painéis internos (ex.: dashboard)
- **lg (1024px+):** 3 colunas para grid de instrutores; mapa lado a lado com lista

### Espaçamento Interno

Usar múltiplos de 4 via Tailwind (`gap-4`, `p-4`, `mt-6`, etc.). Não usar valores arbitrários salvo para matching da logo (ex.: `h-[42px]` para navbar mobile).

### Navbar

- **Mobile:** Logo + hamburger menu (drawer lateral via Chakra `Drawer` com `placement="left"`)
- **Desktop:** Logo + links + avatar dropdown
- Altura fixa: `h-16` (64px)
- Sticky com `shadow-sm` ao scroll
- Background: `bg-white` com `border-b border-la-gray-300`

### Breakpoints Tailwind (padrão, não customizar)

```
sm:  640px   md: 768px   lg: 1024px   xl: 1280px
```

---

## 5. Componentes Core

> Todos os componentes base vêm do **Chakra UI**. Nunca sobrescrever o tema global via `sx` ou `style` inline. Criar componentes wrappers em `/components/` estendendo o tema Chakra com os tokens do LinkAuto. Tailwind CSS é usado para layout, espaçamento e elementos fora do sistema Chakra (ex.: mapa, grids de página).

### 5.1 `InstructorCard`

```
┌─────────────────────────────────────┐
│  [Avatar 56px]  Nome do Instrutor   │
│                 ★★★★☆ 4.2 (38)    │
│                 📍 2,4 km · R$80/h  │
│  [Badge: DETRAN ✓]  [Especialidades]│
│                          [Agendar →]│
└─────────────────────────────────────┘
```

- Card: `rounded-2xl border border-la-gray-300 bg-white p-4 shadow-sm`
- Avatar: `rounded-full ring-2 ring-la-green-light`
- Badge DETRAN: `bg-la-green-light text-la-green-dark text-xs font-medium px-2 py-0.5 rounded-full`
- Botão Agendar: Chakra `<Button colorScheme="laBlue" size="sm">` (ver tema customizado seção 5.7)
- Hover no card: `hover:shadow-md hover:border-la-blue-light transition-shadow duration-200`

### 5.2 `BookingStatusBadge`

```tsx
const statusConfig = {
  PENDENTE:   { label: 'Pendente',   bg: 'bg-amber-100',   text: 'text-amber-700' },
  CONFIRMADA: { label: 'Confirmada', bg: 'bg-la-blue-light', text: 'text-la-blue-dark' },
  REALIZADA:  { label: 'Realizada',  bg: 'bg-la-green-light', text: 'text-la-green-dark' },
  CANCELADA:  { label: 'Cancelada',  bg: 'bg-red-100',     text: 'text-red-700' },
}
```

- Forma: `rounded-full px-3 py-1 text-xs font-medium`
- Sempre acompanha um ícone (Lucide): Clock, CheckCircle2, CheckCheck, XCircle

### 5.3 `BookingStatusTimeline`

Componente visual de progresso horizontal para exibir a state machine do agendamento:

```
● PENDENTE → ● CONFIRMADA → ● REALIZADA
```

- Linha conectora: `bg-la-gray-300` (inativa) / `bg-la-blue` (ativa)
- Nó ativo: `bg-la-blue text-white`
- Nó futuro: `bg-la-gray-100 border border-la-gray-300 text-la-gray-500`
- Nó CANCELADA: aparece em vermelho lateral, fora da linha principal

### 5.4 `RatingStars`

- Estrelas cheias: `text-amber-400` (ícone `Star` preenchido)
- Estrelas vazias: `text-la-gray-300`
- Tamanho: `w-4 h-4` em cards; `w-5 h-5` em perfil público
- Sempre exibir rating numérico + total entre parênteses: `4.2 (38 avaliações)`

### 5.5 `MessageBubble` (Chat da Reserva)

```
Enviada (direita):   bg-la-blue text-white rounded-2xl rounded-br-sm
Recebida (esquerda): bg-la-gray-100 text-la-gray-900 rounded-2xl rounded-bl-sm
```

- Padding: `px-4 py-2`
- Metadado (horário): `text-xs text-la-gray-500 mt-1`
- Thread containerizada por `booking_id`, não por par de usuários

### 5.6 `SlotPicker`

Grid de botões de horário para seleção de slots:

- Disponível: `border border-la-gray-300 bg-white hover:border-la-blue hover:bg-la-blue-light`
- Selecionado: `bg-la-blue text-white border-la-blue`
- Bloqueado/Reservado: `bg-la-gray-100 text-la-gray-400 cursor-not-allowed opacity-60`
- Validação visual: quando < 2 slots selecionados, exibir `text-amber-600` com aviso de mínimo 2h

### 5.7 Botões (Chakra UI Button — colorSchemes customizados)

O tema Chakra é estendido em `src/theme/index.ts` com dois `colorScheme` próprios do LinkAuto:

```ts
// src/theme/system.ts
import { createSystem, defaultConfig, defineConfig } from "@chakra-ui/react";

const config = defineConfig({
  theme: {
    tokens: {
      colors: {
        laBlue: {
          50: { value: "#EBF4FC" },
          100: { value: "#D6E8F7" },
          500: { value: "#1A6DB5" },
          600: { value: "#165E9C" },
          700: { value: "#124E87" },
        },
        laGreen: {
          50: { value: "#EAF6EF" },
          100: { value: "#D4EFE0" },
          500: { value: "#3EAA5B" },
          600: { value: "#35924D" },
          700: { value: "#2C7D42" },
        },
      },
    },
  },
});

export const appSystem = createSystem(defaultConfig, config);
```

| Variante Chakra | Uso | Props |
|---|---|---|
| `colorScheme="laBlue"` | CTA principal (Agendar, Confirmar) | `variant="solid"` |
| `colorScheme="laGreen"` | Aprovar, Marcar como realizada | `variant="solid"` |
| `colorScheme="red"` | Cancelar, Rejeitar | `variant="solid"` |
| `colorScheme="gray"` | Ações secundárias | `variant="outline"` |
| `colorScheme="gray"` | Nav links, ações terciárias | `variant="ghost"` |

---

## 6. Padrões de Formulário

- Biblioteca: **React Hook Form** + **Zod**
- Componentes: Chakra `Input`, `Select`, `Textarea`, `Checkbox` — sempre dentro de `FormControl` + `FormLabel` + `FormErrorMessage`
- Label sempre acima do input (`mb-1.5 text-sm font-medium text-la-gray-700`)
- Erro inline: via `<FormErrorMessage>` do Chakra (nunca modal)
- Campos obrigatórios: prop `isRequired` no `FormControl` — Chakra renderiza o asterisco automaticamente
- Formulários multi-step (ex.: cadastro de instrutor): usar `@chakra-ui/stepper` (`Stepper`, `Step`, `StepIndicator`, `StepStatus`) ou indicador de progresso com `Progress` do Chakra

### Upload de Documentos

- Área de drop: `border-2 border-dashed border-la-gray-300 rounded-xl p-6 text-center`
- Estado de hover/drag: `border-la-blue bg-la-blue-light`
- Ícone: `Upload` do Lucide, `w-8 h-8 text-la-gray-400`
- Formatos aceitos exibidos: `text-xs text-la-gray-500` — "JPG, PNG ou PDF · Máx. 10 MB"
- Preview após upload: thumbnail para imagem; ícone de PDF para documentos

---

## 7. Mapa (Leaflet)

### Configuração Visual

```ts
// Tile provider recomendado (gratuito, sem API key)
const TILE_URL = 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png'
// Atribuição obrigatória:
// © OpenStreetMap contributors © CARTO
```

> Justificativa: CartoDB Light combina com a paleta neutra do LinkAuto. Evitar o tile padrão do OSM (visual pesado demais para mobile).

### Marcadores de Instrutor

- Usar `DivIcon` com HTML customizado (não o pin padrão do Leaflet)
- Forma: círculo com avatar ou iniciais, borda `ring-2 ring-la-blue`
- Ao selecionar: ring cresce para `ring-4 ring-la-blue`, `z-index` elevado
- Popup ao clicar: mini `InstructorCard` inline (nome + rating + botão "Ver perfil")

### Círculo de Raio de Atuação

- `<Circle>` do react-leaflet
- Cor: `color: '#1A6DB5'`, `fillColor: '#D6E8F7'`, `fillOpacity: 0.2`, `weight: 1.5`
- Visível na busca ao hover/select do instrutor e na tela de perfil público

---

## 8. Feedback Visual e Estados

### Loading

- Listas (InstructorCard): Chakra `<Skeleton>` + `<SkeletonCircle>` — 3 cards empilhados, proporção `h-28`
- Dados de perfil: `<SkeletonCircle size="14">` + `<SkeletonText noOfLines={3}>`
- Mapa: Chakra `<Spinner colorScheme="laBlue">` centralizado sobre o container do mapa com `bg-white/70`

### Toasts

- Hook: Chakra `useToast()` — sem dependência externa
- Sucesso: `status="success"`, `colorScheme="laGreen"` + mensagem curta (< 8 palavras)
- Erro: `status="error"`, `colorScheme="red"`
- Info: `status="info"`, `colorScheme="laBlue"`
- Posição: `position="bottom"` em mobile; `position="bottom-right"` em desktop
- Duração: `duration={4000}` padrão; `duration={6000}` para erros
- Sempre `isClosable: true`

### Estados Vazios

- Busca sem resultados: ilustração SVG simples (mapa com lupa) + texto + sugestão de ampliar raio
- Lista de agendamentos vazia: ilustração de calendário + CTA "Buscar instrutores"
- Chat sem mensagens: "Nenhuma mensagem ainda. Inicie a conversa!" centralizado com `text-la-gray-500`

### Penalidade de Cancelamento

Banner de alerta dentro de `/bookings/new` quando `student.is_blocked = true`:

```
⚠️  Sua conta está com reservas bloqueadas até [data].
    Cancelamentos com menos de 24h de antecedência resultam em bloqueio de 7 dias.
```

- Componente: Chakra `<Alert status="error">` + `<AlertIcon>` + `<AlertDescription>`, com link "Saiba mais" via Chakra `<Link colorScheme="red">`

---

## 9. Identidade Visual — Uso da Logo

### Versões

| Contexto | Arquivo | Regra |
|---|---|---|
| Navbar (desktop) | Logo completa horizontal | Máx. `h-10` |
| Navbar (mobile) | Apenas símbolo LA | `h-8 w-8` |
| Splash / Loading | Logo completa + subtítulo | Centralizada |
| Favicon | Símbolo LA simplificado | 32×32px |
| Emails SES | Logo completa em PNG (fundo branco) | Máx. 200px de largura |

### Regras

- Nunca distorcer a proporção da logo.
- Nunca aplicar sobre fundos coloridos sem versão alternativa (branca).
- Espaçamento mínimo ao redor: equivalente à altura da letra "L" do símbolo.
- Não recolorizar: usar apenas as versões oficiais (azul+verde ou monocromática).

---

## 10. Acessibilidade

- Contraste mínimo WCAG AA: todos os textos sobre backgrounds da paleta foram verificados.
  - `#1A6DB5` sobre branco: ✅ ratio 4.8:1
  - `#3EAA5B` sobre branco: ✅ ratio 4.5:1 (usar peso 500+ para texto pequeno)
  - `#374151` (gray-700) sobre branco: ✅ ratio 8.9:1
- Todos os botões Chakra já têm `focusVisible` ring por padrão — garantir que o tema não remova o `_focusVisible` style dos componentes customizados
- Ícones puramente decorativos: `aria-hidden="true"`
- Ícones com significado semântico (ex.: status): `aria-label` obrigatório
- Inputs: sempre `<label>` associado via `htmlFor` — nunca apenas placeholder
- Mapa Leaflet: incluir `aria-label="Mapa de instrutores disponíveis"` no container

---

## 11. Diretrizes para o Desenvolvimento do Frontend

> Instruções específicas e governança de desenvolvimento de novas telas e funcionalidades do LinkAuto.

### O que o Desenvolvedor / IA DEVE fazer

- Usar `className` com tokens Tailwind `la-*` ou espaçamentos/layouts padrão apenas para a estrutura — toda a estilização visual de componentes UI (textos, painéis, cores) deve ser feita usando as props nativas do Chakra UI v3.
- Usar **DM Sans** em todo texto UI (configurado no tema Chakra v3 via `fonts.heading` e `fonts.body` em `system.ts`).
- Criar e estender componentes no padrão **Chakra UI v3 Composition API** (ex.: `*.Root`, `*.Trigger`, `*.Content`, `*.CloseTrigger`).
- Sempre adotar **Tokens Semânticos** (ex.: `text.primary`, `surface.canvas`, `brand.solid`) ao invés de cores hexadecimais explícitas, garantindo que o dark mode nativo funcione automaticamente.
- Usar Lucide React para ícones, integrando-os de forma harmoniosa com o Chakra UI.
- Empregar o hook `useColorMode` do Chakra v3 e o `<ThemeProvider>` configurado no `router.tsx` e `main.tsx` para alternância de temas.
- Criar e evoluir as regras de estado global exclusivamente no store **Zustand** (`sessionStore`).
- Implementar **Test-Driven Development (TDD)** usando a suíte ativa de Vitest + React Testing Library antes de qualquer refatoração.

### O que NÃO deve ser feito

- Usar `style={{}}` inline para cores, tipografias ou espaçamentos.
- Criar ou injetar variáveis globais fora do `theme/system.ts`.
- Tentar injetar pacotes CSS adicionais sem a devida validação do Tech Lead.
- Sobrescrever manualmente elementos internos de tema com seletores de classe rígidos do CSS.
- Utilizar mocks hardcoded nas páginas quando existirem endpoints operacionais prontos no backend da aplicação.

### Governança de Skills, Agentes & MCP Tools Recomendadas

Consulte o documento completo [FRONTEND_RECOMMENDATIONS.md](file:///home/gabrieldnsilva/projects/LinkAuto-APP/docs/FRONTEND_RECOMMENDATIONS.md) para detalhes de instalação e uso no LinkAuto.

| Recurso | Tipo | Função no LinkAuto |
| :--- | :--- | :--- |
| `@frontend-design` / `@web-design-guidelines` | **Skill** | Fidelidade estética mobile-first e padrões premium baseados no `DESIGN.md`. |
| `@test-driven-development` | **Skill** | Orientação do ciclo TDD Red-Green-Refactor com Vitest. |
| `@ui-a11y` / `@wcag-audit-patterns` | **Skill** | Auditoria e correções de acessibilidade para navegação acessível. |
| `@context7-mcp` (`context7`) | **MCP Tool** | Consultas ao vivo de documentação técnica oficial das APIs do **Chakra UI v3** e **Tailwind CSS 4** para evitar código depreciado. |
| `research` | **Agent** | Investigação de contratos de API e modelos Pydantic no backend. |
| `self` | **Agent** | Subagente isolado para refatoração e testes de componentes específicos. |

---

## 12. Referências e Recursos

- Logo e banner: `docs/images/LinkAuto-banner.webp`
- Data model: `specs/001-user-booking-domains/data-model.md`
- Spec completo: `specs/001-user-booking-domains/spec.md`
- Compliance: `specs/001-user-booking-domains/compliance.md`
- Chakra UI: <https://chakra-ui.com/docs/getting-started>
- DM Sans (Google Fonts): <https://fonts.google.com/specimen/DM+Sans>
- CartoDB tiles: <https://carto.com/basemaps>
- react-leaflet: <https://react-leaflet.js.org>
- Lucide React: <https://lucide.dev>

---

*Última atualização: 2026-04-18 — LinkAuto v0.1 MVP Demo*
*Manter este documento sincronizado com mudanças de paleta, tipografia ou padrões de componente.*
