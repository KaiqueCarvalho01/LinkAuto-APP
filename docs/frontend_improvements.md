Todas as propostas mencionadas estarão localizadas em linkauto-frontend/

/home/gabrieldnsilva/projects/LinkAuto-APP/docs/DESIGN.md é referência de DESIGN.

Recomendações de Skills:
      •  @frontend-design  &  @web-design-guidelines  para fidelidade estética do  DESIGN.md  e interfaces premium.
      •  @ui-a11y  &  @wcag-audit-patterns  para garantia de acessibilidade WCAG 2.2 AA nos fluxos interativos.
      •  @test-driven-development  para manter nossa suíte Vitest blindada no ciclo Red-Green-Refactor.
      •  @zustand-store-ts  para as regras de gerenciamento do  sessionStore .

Recomendações de MCP Tools:
      • O uso estratégico do  @context7-mcp  (context7) para extrair dinamicamente a documentação atualizada do
      Chakra UI v3 e Tailwind CSS 4, eliminando alucinações de sintaxe de APIs recentes.

Recomendações de Agentes:
      • O uso do agente  research  de forma assíncrona para validar os contratos de API Pydantic do backend sem
      bloquear a escrita de código.
      • O agente  self  para isolar grandes refatorações críticas em sub-branches dedicadas.

1 - Em `Home.tsx` (landpage) após remover o mockData, não temos mais um "preview" de como o sistema de busca funcionará. Agora temos somente um mapa vazio do leaflet.
Proposta: Voltar a mockar dados fictícios para realização dessa preview do funcionamento do sistema ou utilizar os endpoints de search (com queries pré-definidas) para mostrar os instrutores disponíveis em uma região.

2 - Em `Home.tsx` o texto "conexão certa." poderia trabalhar junto com um typewritter dinâmico (animação) alternando para  6 frases que façam sentido dentro do contexto da aplicação, finalizando o ciclo com "LinkAuto" nos padrões visuais da logo. 

3 - Em `Home.tsx` o botão "Ver Busca Demo" é redundante em relação ao "Acessar Plataforma". Ambos redirecionam para login.
Proposta: "Ver Busca Demo" poderia ser substituído por "Ver instrutores disponíveis" (ou algo semelhante) considerando a ideia de perfil público de instrutores que já está no escopo. Seria uma função diferente da busca através de geolocalização, mas traz ênfase de que a plataforma já é consolidada com instrutores, levando a um aspecto mais profissional e sem interações múltiplas que levam ao mesmo lugar.

4 - Em `ProfileSidebar.tsx` a página "/agendamentos" não existe mais. Quando o botão "Minhas Aulas" é selecionado, o usuário é redirecionado para a Home.
Proposta: A rota correta aparentemente é "/my-lessons". Podemos realizar a troca simples.

5 - `InstructorDashboard.tsx` aparentemente não está sendo utilizado, pois não temos um dashboard propriamente para os instrutores (e isso faz parte dos requisitos da aplicação).
Proposta: Estabelecer o uso adequado de um dashboard para instrutores, atualmente em `Footer.tsx`temos uma rota para /instructor/students que não funciona. Esta roda com dashboard de instrutores também será implementada no `Profile.tsx`específicamente no perfil de instrutor.

6 - Um instrutor funcional (operacional na plataforma) deve ter TODOS os dados obrigatoriamente preenchidos na plataforma para que o mesmo esteja disponível para seleção no /search por alunos. Porém, em `Profile.tsx` (/profile) atualmente não estamos seguindo o fluxo de cadastro completo de instrutores e alunos. 
Contando apenas com: [Nome, Telefone, Localização, Valor por Hora, Raio de Atuação, Biografia]. Todos devem ser preservados, mas é necessário o preenchimento completo do perfil, seja de alunos quanto de instrutores.
Proposta: Seguir o que temos em `/home/gabrieldnsilva/projects/LinkAuto-APP/linkauto-backend/app/models/user.py` para o preenchimento completo do perfil, assim como habilitar os uploads de documentações para que o administrador aprove posterioemente. PODE SER necessário adicionar uma nova rota para o preenchimento completo do perfil ou adotar outra estratégia. E este preenchimento deve ser persistido no sistema, com validações necessárias antes de ser enviado ao backend.

7 - Em `Profile.tsx` - No perfil de instrutor, "Buscar Instrutores" pode não ser necessário se o instrutor não possuir a role de "Aluno".
Proposta: Validar se o perfil acessado possui role: aluno, para que a experiência seja personalizada com base no que o usuário busca na plataforma, removendo artefatos desnecessários e que não serão utilizados por ele. (em seções próprias como perfil)

8 - Em `Profile.tsx` o botão "Segurança e senha" não possui rota / interface para alteração e recuperação de senha.
Proposta: Conectar o endpoint /api/v1/auth/password-reset e criar página para recuperação de senha. Como o sistema não está em produção, muitos e-mails não são válidos, mas para fins de testes, podemos adotar a estratégia de envio de e-mail com token único para a recuperação de senha. Assim podemos validar também se o serviço AWS SES está funcionando corretamente.

9 - `/home/gabrieldnsilva/projects/LinkAuto-APP/linkauto-frontend/src/app/router.tsx` Está atualmente renderizando a rota /admin/instructors. Sua interface é extremamente simples e não corresponde ao esperado da página de administrador, o qual no plano de desenvolvimento deve possuir também uma dashboard completa com informações corretas da plataforma e um fluxo de aprovação de instrutores coerente com o planejado. 
Proposta: Analisar a necessidade da renderização da página de admin à partir do arquivo router. Adequar a interface e funcionalidades necessárias para o fluxo completo como admin ser realizado de forma coerente com as documentações e os planos estipulados na documentação da aplicação. 

10 - Na rota /my-lessons, erro utilizar o botão "Cancelar Aula": "NetworkError when attempting to fetch resource." O botão não está operacional, e à partir do NetWorkError, o botão não fica mais "interagível"
Proposta: Validar se o endpoint está correto e funcionando adequadamente, para que seja permitido que os alunos cancelem suas aulas sem intervenção de um administrador, gerando uma melhor experiência no geral.

