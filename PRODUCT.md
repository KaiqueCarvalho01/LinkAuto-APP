# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

1. **Alunos:** Candidatos à primeira habilitação (CNH categorias A/B) ou motoristas já habilitados buscando aulas práticas para aperfeiçoamento, perda do medo de dirigir (amaxofobia) ou reciclagem.
2. **Instrutores Autônomos:** Instrutores de trânsito credenciados pelo DETRAN que oferecem treinamento veicular prático independente.
3. **Administradores:** Moderadores responsáveis pela auditoria documental e validação regulatória do credenciamento DETRAN dos instrutores.

## Product Purpose

Conectar alunos a instrutores de direção veicular credenciados através de busca geolocalizada, visualização de disponibilidade de horários e agendamento seguro, democratizando o treinamento veicular prático no Brasil.

## Positioning

A plataforma de conexão direta e transparente para aulas práticas de direção no Brasil, combinando validação rigorosa de credenciamento DETRAN, privacidade estrita (LGPD com proteção de identificadores via slugs) e agendamento direto sem taxas opacas de intermediação financeira no MVP (V1).

## Operating Context

- Aplicação web responsiva orientada a dispositivos móveis (*mobile-first*).
- Busca baseada em geolocalização e raio de atuação (km) em cidades brasileiras.
- Grade de disponibilidade em slots de 1 hora, com agendamentos de no mínimo 2 horas consecutivas.
- Chat assíncrono de comunicação direta entre aluno e instrutor atrelado ao ciclo de vida da reserva.

## Capabilities and Constraints

- **RN01 (Visibilidade Condicional):** Instrutores permanecem invisíveis na busca e mapa até terem sua credencial e documentos validados por um Administrador.
- **RN02 (Privacidade Documental):** Documentos de validação (CNH, credencial DETRAN) armazenados no bucket S3 são expurgados após análise administrativa.
- **RN03 (Regra de Agendamento):** Slots horários de 1h; agendamentos exigem seleção mínima de 2 slots contíguos.
- **RN04 (Política de Cancelamento):** Cancelamento livre com até 24h de antecedência. Cancelamentos com menos de 24h geram bloqueio de novas reservas por 7 dias.
- **RN05 (Comunicação):** Mensageria assíncrona estritamente associada a uma reserva existente (sem WebSockets na V1).
- **RN06 (Pagamentos):** A versão V1 NÃO processa pagamentos nem armazena ou exibe transações financeiras na plataforma.
- **LGPD & Segurança:** Nenhuma rota pública expõe UUIDs internos de usuários; a identificação externa é feita exclusivamente por slugs públicos.

## Brand Commitments

- **Nome:** LinkAuto.
- **Idioma da Interface:** Português do Brasil (PT-BR).
- **Cores Oficiais:** `laBlue` (azul confiança institucional), `laGreen` (verde progresso/aprovação) e superfícies neutras de alto contraste.
- **Identidade de Tom:** Profissional, confiável, acolhedor e focado na segurança do trânsito.

## Product Principles

1. **Segurança e Conformidade Regulatória:** Apenas profissionais com credencial DETRAN auditada interagem com alunos.
2. **Privacidade por Padrão (LGPD):** Dados pessoais e sensíveis são protegidos e expurgados conforme a necessidade.
3. **Agendamento Claro e Previsível:** Regras de cancelamento, antecedência e horários são explícitas em todas as etapas da jornada.
4. **Design Mobile-First e Acessível:** Interfaces enxutas, sem ruído estético artificial, em estrita conformidade com WCAG 2.1 AA.

## Accessibility & Inclusion

Conformidade com diretrizes WCAG 2.1 AA: contraste semântico adaptável a Light e Dark Mode, alvos de toque mínimos de 44x44px em telas sensíveis ao toque, e semântica acessível com suporte a leitores de tela.
