# 🚀 Frontend Development Blueprint: Skills, Agents & MCP Tools

Como **Senior Software Engineer & Tech Lead**, apresento o mapeamento estratégico de ferramentas recomendadas para o desenvolvimento de novas funcionalidades e otimização do ecossistema frontend do **LinkAuto** (`linkauto-frontend`).

Este documento serve como referência de arquitetura de ferramentas e processos para guiar os engenheiros do time no desenvolvimento ágil, focado em **TDD**, **Clean Code** e **Premium Visual Design**.

---

## 🏛️ Contexto da Stack do Frontend do LinkAuto
Nossa arquitetura de frontend baseia-se em tecnologias modernas e de alta performance:
*   **Runtime & Framework:** React 19.2 + Vite
*   **TypeScript:** v5.9 (Strict mode rigoroso)
*   **Design & UI:** Chakra UI v3 (`@chakra-ui/react@3.x` com Composition API e Tokens Semânticos) + Tailwind CSS 4 + Lucide React
*   **Estado:** Zustand (com `sessionStore`)
*   **Mapas:** Leaflet & react-leaflet
*   **Testes:** Vitest + Testing Library + Playwright

Para evoluir e manter essa stack com segurança e alta fidelidade visual, recomendamos a adoção das seguintes **Skills**, **Agentes** e **MCP Tools**.

---

## 🛠️ 1. Recomendações de Skills

As **Skills** são pacotes de especialização pré-configurados que estendem o entendimento das IAs no desenvolvimento de tarefas específicas. Para o nosso frontend, as mais valiosas são:

### A. Design System & Fidelidade Visual
*   **`@frontend-design` & `@web-design-guidelines`**
    *   **Por que usar:** O LinkAuto exige um visual rico e premium (definido no [DESIGN.md](file:///home/gabrieldnsilva/projects/LinkAuto-APP/docs/DESIGN.md)), evitando layouts genéricos e cores sem harmonia.
    *   **Benefício técnico:** Garante a aplicação correta dos tokens semânticos do Chakra UI v3, responsividade mobile-first consistente e consistência visual geral sem a proliferação de classes ad-hoc do Tailwind.
*   **`@design-spells`**
    *   **Por que usar:** Adiciona micro-interações, transições fluidas e estados interativos diferenciados nos agendamentos de slots e visualizações de mapas.
    *   **Benefício técnico:** Eleva o engajamento e a percepção de produto premium (WOW factor).

### B. Acessibilidade (a11y) & Usabilidade
*   **`@ui-a11y` & `@wcag-audit-patterns`**
    *   **Por que usar:** Nossos componentes interativos de calendário, listas de instrutores e modais devem ser acessíveis a todos os usuários.
    *   **Benefício técnico:** Validação em conformidade com as diretrizes do WCAG 2.2 AA, garantindo navegação por teclado e semântica correta usando as tags nativas do Chakra UI v3 (ex: `*.Root`, `*.Trigger`).

### C. Qualidade & Testes (TDD)
*   **`@test-driven-development` & `@tdd-workflows-tdd-cycle`**
    *   **Por que usar:** O frontend do LinkAuto possui uma robusta suíte de testes com Vitest e React Testing Library que garante a integridade dos componentes diante de novos refinamentos.
    *   **Benefício técnico:** Auxilia no ciclo *Red-Green-Refactor*, evitando que novos componentes quebrem fluxos legados e ajudando na criação de cenários de testes assíncronos complexos (como requisições e limpezas de `useEffect`).
*   **`@zustand-store-ts`**
    *   **Por que usar:** O gerenciamento do estado de login e sessão ativa depende do Zustand.
    *   **Benefício técnico:** Guia a modelagem segura do Zustand Store em TypeScript estrito, prevenindo bugs de sincronização de estado com o `sessionStorage`.

---

## 🔌 2. Recomendações de MCP (Model Context Protocol)

O **MCP** permite que IAs busquem dados externos atualizados dinamicamente, superando a barreira da base de dados estática do modelo de IA.

### A. `@context7-mcp` (context7)
*   **Por que usar:** O frontend do LinkAuto utiliza bibliotecas em suas versões mais recentes e disruptivas: **Chakra UI v3** e **Tailwind CSS 4**. Ambas mudaram radicalmente a sintaxe em relação às versões v2 e v3, respectivamente (ex: Chakra v3 utiliza novas APIs de composição de tags e abandona propriedades legadas; Tailwind 4 tem nova arquitetura baseada inteiramente em CSS).
*   **Benefício técnico:** Ao invocar a ferramenta MCP do `context7`, a IA consegue ler a documentação de API ao vivo das bibliotecas diretamente da web. Isso **elimina alucinações de sintaxe**, evita o uso de padrões obsoletos (deprecated) e acelera o tempo de desenvolvimento impedindo erros de compilação ou build causados por códigos legados sugeridos pela IA.

---

## 🤖 3. Recomendações de Agentes Autônomos

Dividir o trabalho de grandes tarefas de frontend utilizando subagentes reduz o consumo de janelas de contexto e aumenta a assertividade técnica.

### A. Subagente de Pesquisa (`research`)
*   **Por que usar:** O frontend do LinkAuto consome dados de uma API REST robusta desenvolvida em FastAPI. Modificações de layout frequentemente necessitam de validações de schemas no backend.
*   **Benefício técnico:** O desenvolvedor pode delegar para o agente `research` a leitura de contratos e validações de tipos do Pydantic no código do backend (`linkauto-backend`) em segundo plano, enquanto o agente principal continua programando e renderizando o frontend sem interrupções.

### B. Subagente de Refatoração Isolada (`self` em workspace clonado)
*   **Por que usar:** Grandes refatorações de componentes pesados (ex: a tela de mapa de instrutores ou o calendário de agendamento) podem desestabilizar a branch principal se feitas de uma só vez.
*   **Benefício técnico:** Permite isolar um subagente de nível `self` em uma sub-branch limpa para criar provas de conceito de componentes isolados, testar performance de re-renderizações e integrar APIs complexas.

---

## 📈 Tabela de Resumo & Decisão

| Tipo | Nome | Foco | Cenário de Uso Recomendado |
| :--- | :--- | :--- | :--- |
| **Skill** | `@frontend-design` | Fidelidade Visual | Criação de novos modais, cards e layouts mobile-first. |
| **Skill** | `@test-driven-development` | Qualidade & TDD | Correção de bugs e escrita de novos fluxos de testes no Vitest. |
| **Skill** | `@ui-a11y` | Acessibilidade | Refinamento de novos elementos interativos no fluxo de agendamento. |
| **MCP** | `@context7-mcp` | Documentação Viva | Consultar sintaxe do Chakra UI v3 e propriedades do Tailwind CSS 4. |
| **Agent** | `research` | Investigação Backend | Analisar payloads e mapear endpoints reais de instrutores e horários. |

---
*Este guia técnico de governança deve ser revisado periodicamente pelo time à medida que novas ferramentas e skills forem disponibilizadas.*
