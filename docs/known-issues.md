# 🐛 Frontend Known Issues

*Este documento lista os bugs e melhorias pendentes no frontend. Agente Gemini, ao resolver uma issue, atualize o status deste documento para [RESOLVIDO] e registre a mudança no `progressTracker-frontend.md`.*

## 🎨 UI/UX & Acessibilidade

### Issue #1: Padronização Visual de Grids na Landing Page

- **Status:** [RESOLVIDO]
- **Arquivos Afetados:** `InfoSections.tsx`, `Testimonials.tsx`
- **Descrição:** As seções não possuem delimitação clara entre os itens, dificultando a escaneabilidade da página.
- **Ação Esperada (Acceptance Criteria):** Refatorar utilizando o modelo de Cards já existente em `Home.tsx`. Use `<SimpleGrid>` e aplique *semantic tokens* do Chakra UI v3 (ex: `bg="surface.panel"`, `borderColor="border.subtle"`) para garantir delimitação visual, suporte a ColorMode e acessibilidade (WCAG).

### Issue #2: Falta de Affordance no FAQ

- **Status:** [RESOLVIDO]
- **Arquivos Afetados:** `FAQ.tsx`
- **Descrição:** Não há indicação visual de que as perguntas são clicáveis (falta de affordance).
- **Ação Esperada (Acceptance Criteria):** Substituir o layout atual pelo componente `<Accordion>` do Chakra UI, garantindo a presença de ícones de expansão (chevron) e comportamentos de *hover* claros.

## 🗺️ Camadas e Z-Index (Mapas)

### Issue #3: MapContainer vazando sobre a NavBar (Backdrop Blur)

- **Status:** [RESOLVIDO]
- **Arquivos Afetados:** `InstructorMap.tsx`, `NavBar.tsx`
- **Descrição:** O mapa do Leaflet está sobrepondo a NavBar e ignorando o efeito de `blur`. Nota: em `Home.tsx` o comportamento está correto, o que indica inconsistência de CSS.
- **Ação Esperada (Acceptance Criteria):** Inspecionar a hierarquia e o `z-index` dos componentes. Garantir que o container do mapa tenha um `z-index` inferior (ex: `z-index={0}`) e que a NavBar possua o `z-index` correto (ex: `z-index={500}`) com `position="sticky"` ou `"fixed"`.

### Issue #4: Sobreposição do Leaflet no Overlay da Sidebar (Guerra de Z-Index)

- **Status:** [RESOLVIDO]
- **Arquivos Afetados:** `SearchPage.tsx`, `InstructorMap.tsx`, `ProfileSidebar.tsx`
- **Descrição:** Na rota `/search`, ao abrir a `ProfileSidebar`, o fundo da tela escurece (backdrop overlay), mas o mapa (Leaflet) continua em alto contraste, ignorando o overlay e sobrepondo-o.
- **Ação Esperada (Acceptance Criteria):** Inspecionar e isolar o contexto de empilhamento (stacking context). Garantir que o `z-index` do Drawer/Sidebar e do seu respectivo overlay (Chakra UI) seja superior ao `z-index` global do container do Leaflet (que geralmente exige um valor > 400 para ser coberto) ou diminuir o z-index base do mapa.

## 🌓 ColorMode (Tema Claro/Escuro)

### Issue #5: Ausência de Fundo Sólido no ProfileSidebar (Modo Claro)

- **Status:** [RESOLVIDO]
- **Arquivos Afetados:** `ProfileSidebar.tsx`
- **Descrição:** No ColorMode claro, o container principal da sidebar fica sem cor de fundo (transparente). Isso faz com que os textos e ícones (ex: "Minhas Aulas", "Sair") fiquem soltos visualmente sobre o restante da página ofuscada, arruinando o contraste.
- **Ação Esperada (Acceptance Criteria):** Definir explicitamente a propriedade de background (`bg` ou `backgroundColor`) no container principal da `ProfileSidebar` utilizando *semantic tokens* responsivos ao tema do Chakra UI (ex: `bg="surface.panel"` ou uma cor base como `gray.50`). Validar o contraste do texto (`color="text.primary"`) contra este novo fundo.

### Issue #6: Página de Login Incompatível com Temas

- **Status:** [RESOLVIDO]
- **Arquivos Afetados:** `Login.tsx`
- **Descrição:** A maior parte dos elementos da página de login não se adaptam à troca de tema (Claro/Escuro), resultando em mau contraste.
- **Ação Esperada (Acceptance Criteria):** Auditoria completa do arquivo para remover estilização engessada. Implementar variáveis de cor responsivas ao tema do Chakra UI, seguindo a diretriz do projeto (ex: usar `text.muted`, `brand.500`, etc).
