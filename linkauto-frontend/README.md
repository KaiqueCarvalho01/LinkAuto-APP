# LinkAuto Frontend 🚗⚡

Interface web moderna, responsiva e *mobile-first* desenvolvida com **React 19**, **Chakra UI v3**, **Tailwind CSS 4** e **TypeScript 5.9 (Strict)** para a plataforma **LinkAuto**, especializada no agendamento e conexão de instrutores autônomos de trânsito credenciados com alunos.

---

## 🏛️ Visão Geral da Arquitetura

O frontend do LinkAuto foi desenhado com foco nos princípios **Clean Architecture**, **SOLID** e no padrão **TDD (Test-Driven Development)** com Vitest. A estrutura de diretórios separa claramente UI, estado, serviços de API e temas:

```text
linkauto-frontend/
├── src/
│   ├── app/             # Configuração da aplicação e roteamento principal (router.tsx)
│   ├── components/      # Componentes reutilizáveis (Navbar, Footer, InstructorCard, SlotPicker, etc.)
│   │   └── landing/     # Seções modulares da landing page (Hero, InfoSections, FAQ, Testimonials)
│   ├── features/        # Regras de domínio e lógica de negócios (bookingRules, etc.)
│   ├── pages/           # Telas da aplicação (Home, SearchPage, LessonDetails, Profile, Dashboards)
│   │   ├── instructors/ # Páginas informativas para instrutores (Benefits, HowItWorks, Simulator)
│   │   └── students/    # Páginas informativas para alunos (FirstLicense, LicensedDrivers, HowItWorks)
│   ├── services/        # Camada de integração HTTP com backend (mappers snake_case -> camelCase)
│   ├── state/           # Gerenciamento de sessão e contexto de autenticação (sessionStore.tsx)
│   ├── test/            # Setup de testes do Vitest, fixtures e helpers de renderização
│   ├── theme/           # Sistema de design tokens, cores semânticas e configuração do Chakra v3
│   └── types/           # Interfaces TypeScript estritas (api.types, instructor, booking, session)
├── scripts/             # Scripts utilitários de manutenção
├── package.json         # Scripts npm e dependências do projeto
├── tsconfig.json        # Configuração estrita do compilador TypeScript (exactOptionalPropertyTypes)
└── vite.config.ts       # Configuração do Vite e Vitest
```

---

## 🎨 Design System & Padrões de Interface

O LinkAuto adota a direção estética **Refined Civic Tech** definida no [`docs/DESIGN.md`](../docs/DESIGN.md):

- **Chakra UI v3 Composition API:** Uso obrigatório de componentes compostos (`*.Root`, `*.Trigger`, `*.Content`, `*.Item`) e `colorPalette`, evitando sintaxes legadas do Chakra v2.
- **Tokens Semânticos:** Cores de status e superfícies utilizam tokens do tema (`bg.muted`, `text.primary`, `border.subtle`), garantindo suporte nativo a tema claro e escuro.
- **Tailwind CSS 4:** Utilizado estritamente para estruturação de layout, espaçamentos, flexbox e grids responsivos.
- **Mapas Interativos:** Integração com **Leaflet** e **react-leaflet** para busca geoespacial e visualização de instrutores em Mogi Mirim e região.
- **Ícones:** Padronizados com a biblioteca **Lucide React**.

---

## 🧭 Roteamento & Navegação Segura (Slugs Públicos)

O roteamento da aplicação é gerenciado pelo **React Router DOM 7** (`src/app/router.tsx`) com divisão clara entre rotas públicas e protegidas por perfil:

### 1. Rotas Públicas & Desacopladas (Visitantes e Alunos)
- `/`: Landing page institucional com animação dinâmica de typewriter, seções informativas e mapa de demonstração.
- `/instructors/:slug`: Perfil público do instrutor acessível anonimamente via **slug seguro e amigável** (ex: `/instructors/camila-rocha-mogi-mirim-8f2a`), com badges DETRAN, bio, especialidades e avaliações reais. Oculta 100% de UUIDs internos e dados sensíveis (LGPD).
- `/students/:slug`: Perfil público do aluno exibindo histórico resumido de aulas concluídas e reputação mútua.
- `/login` e `/register`: Autenticação e cadastro multi-role (Aluno e Instrutor) com formulários validados.
- `/password-reset`: Solicitação pública de redefinição de senha integrada ao backend.

### 2. Rotas Protegidas (`<ProtectedRoute>`)
- `/search`: Busca geolocalizada de instrutores no mapa e lista com filtros por especialidade e ordenação.
- `/my-lessons`: Painel de acompanhamento de agendamentos (`PENDENTE`, `CONFIRMADA`, `REALIZADA`, `CANCELADA`) com confirmação de cancelamento inline.
- `/lessons/:id`: Detalhes do agendamento com chat de mensagens assíncronas e avaliação mútua pós-aula.
- `/profile`: Configurações privadas e edição dos dados da própria conta autenticada.
- `/admin/instructors`: Dashboard administrativo com métricas operacionais ao vivo e moderação de credenciamento.
- `/instructor/dashboard`: Dashboard dedicado do instrutor com estatísticas de horas e aulas ministradas.

---

## 🔒 Camada de Serviços & Tipagem Estrita

- **Mapeamento de Dados (DTO Mappers):** Todas as chamadas para a API FastAPI convertem payloads `snake_case` em modelos tipados `camelCase` em TypeScript (`src/services/`), tratando valores nulos e strings vazias para resiliência de UI.
- **Renovação Silenciosa de Token:** O interceptor HTTP (`src/services/httpClient.ts`) gerencia automaticamente a rotação de `refresh_token` trafegado em cookies seguros `HttpOnly` em caso de respostas `401 Unauthorized`.
- **TypeScript Strict Mode:** O projeto opera com conformidade máxima no `tsconfig.json`:
  - `exactOptionalPropertyTypes: true`
  - `noUncheckedIndexedAccess: true`

---

## 🛠️ Como Executar o Frontend

### Requisitos
- **Node.js**: v20+ ou v22+
- **npm**: v10+

### Instalação e Execução Local
1. Instale as dependências:
   ```bash
   npm install
   ```

2. Inicie o servidor de desenvolvimento com hot-reload (Vite):
   ```bash
   npm run dev
   ```
   Acesse a aplicação em [http://localhost:5173](http://localhost:5173).

3. Construção para Produção:
   ```bash
   npm run build
   ```

---

## 🧪 Qualidade, Linter e Testes Automatizados

O frontend segue rigorosamente o ciclo **TDD** com cobertura de componentes, regras de domínio e integração:

### 1. Suíte de Testes Unitários e de Componentes (Vitest)
```bash
# Executar todos os testes uma vez
npm run test

# Executar com relatório de cobertura de código
npm run test:coverage
```

### 2. Verificação Estrita de Tipos (TypeScript)
```bash
npm run typecheck
```

### 3. Análise Estática de Código (ESLint)
```bash
npm run lint
```

### 4. Validação Visual & E2E no Navegador
Os fluxos de ponta a ponta (E2E) e a fidelidade visual de renderização de componentes são verificados diretamente via **Chrome DevTools MCP** (`@browser-testing-with-devtools`), proporcionando validação de viewport, inspeção de DOM e capturas de tela determinísticas sem necessidade de runners externos.
