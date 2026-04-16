# Documento de Requisitos — LinkAuto

**Plataforma de Agendamento de Instrutores de Trânsito Autônomos**
Fatec Mogi Mirim — ADS — 2026
Versão: 0.1 (rascunho)

---

## 1. Visão Geral

O **LinkAuto** é uma plataforma web com foco mobile que conecta instrutores de trânsito autônomos credenciados pelo DETRAN a usuários que desejam agendar aulas práticas de direção. A plataforma atende dois públicos:

- **Candidatos à CNH:** em processo de habilitação, beneficiados pela Resolução CONTRAN nº 1.020/2025, que permite aulas práticas com instrutores autônomos fora do vínculo obrigatório com autoescolas.
- **Condutores habilitados:** que buscam aulas de reforço em habilidades específicas (ex.: baliza, direção defensiva, rodovias).

O produto oferece funcionalidades de busca geolocalizada, agendamento, avaliação mútua, mensagens vinculadas ao agendamento e notificações, com foco em segurança, transparência e praticidade para ambas as partes.

---

## 2. Atores do Sistema

| Ator | Descrição |
|---|---|
| **Aluno** | Usuário (habilitando ou condutor habilitado) que busca, agenda e avalia instrutores. |
| **Instrutor Autônomo** | Profissional credenciado pelo DETRAN que gerencia sua agenda, disponibiliza horários e recebe/faz avaliações. |
| **Administrador** | Responsável pela moderação da plataforma, validação manual de credenciamentos e suporte. |

---

## 3. Requisitos Funcionais (RF)

### RF01 — Gestão de Usuários

- CRUD completo de alunos e instrutores
- Autenticação via JWT
- Dois tipos de perfil: Aluno, Instrutor e Admin (com privilégios de moderação) - Usuários podem possuir todos os perfis (ex.: um instrutor também pode ser aluno), mas o cadastro de instrutor requer validação manual do admin para garantir credenciamento legítimo.
- Cadastro de aluno é composto por nome, email, senha, telefone, cidade, estado, tipo de habilitação (se aplicável) e foto de perfil (opcional)
- Cadastro de instrutor é composto por nome, email, senha, telefone, cidade, estado, especialidades (ex.: baliza, rodovias), preço por hora, foto de perfil (opcional), status de credenciamento DETRAN (validado ou pendente), certidão negativa de antecedentes criminais, instrutor deve definir raio de atuação (ex.: 10km) para aparecer nos resultados de busca geolocalizada.
- Senhas armazenadas com bcrypt para segurança
- Validação de dados no frontend e backend para garantir integridade e segurança
- Interface de administração para moderação de usuários e validação de instrutores
- Suporte a recuperação de senha via email

### RF02 — Busca Geolocalizada

- Localizar instrutores próximos à posição do aluno (geolocalização via navegador ou endereço manual)
- Filtros: avaliação média, preço por hora, disponibilidade, região de atuação
- Resultados em lista, filtros de ordenar por distância, preço ou avaliação
- Consultas geoespaciais implementadas com PostGIS no PostgreSQL para garantir desempenho
- Uso de Leaflet para visualização de mapas no frontend com React e Tailwind CSS para responsividade

### RF03 — Perfil Público do Instrutor

- Dados visíveis antes do agendamento: foto, bio, especialidades, região, preço/hora, avaliação média
- Exibir status de credenciamento validado
- Histórico de avaliações recebidas
- Opção de contato (mensagem vinculada a um agendamento) para esclarecer dúvidas antes de reservar uma aula
- Botão de "Agendar Aula" para iniciar o processo de reserva, levando o usuário para a tela de seleção de horário e local.
- Exibir disponibilidade em tempo real para evitar conflitos de agendamento
- Mostrar avaliações e comentários de alunos anteriores para ajudar na decisão de reserva

### RF04 — Gestão de Agenda

- Instrutor define slots de horários disponíveis, incluindo data, hora, local e duração (mínimo 2 horas conforme RN02)
- Aluno visualiza disponibilidade em tempo real e realiza reserva.
- Confirmação ou recusa pelo instrutor com notificação automática. (Até 24h para resposta, após o período o sistema cancela automaticamente para evitar bloqueio de horários e notifica o aluno sobre a indisponibilidade do instrutor)
- Bloqueio automático de horários sobrepostos para o instrutor (RN03).
- Suporte a múltiplos locais de aula (ex.: residência do aluno, estacionamento, via pública) com geolocalização para facilitar a escolha.
- Agenda do instrutor atualizada em tempo real para refletir reservas, cancelamentos e disponibilidade.

### RF05 — Sistema de Agendamento

- Fluxo: busca → seleção de instrutor → escolha de horário/local → confirmação → realização → avaliação
- Na busca é possível visualizar a área de atuação do instrutor no mapa, facilitando a escolha para alunos que preferem aulas próximas ás suas preferências de localização.
- Registro de aula com data, horário, local e status.
- Suporte a cancelamentos com regras de antecedência (ver RN04).
- Status de aula: agendada, confirmada, realizada, cancelada.
- Notificações automáticas para eventos de agendamento (novo agendamento, confirmação, lembrete, cancelamento).
- Interface de gerenciamento de agendamentos para alunos e instrutores, permitindo visualização, edição e cancelamento de aulas.

### RF06 — Sistema de Avaliação Mútua

- Após cada aula, o aluno avalia o instrutor (1–5 estrelas + comentário)
- Após cada aula, o instrutor avalia o aluno (1–5 estrelas + observações)
- Avaliações influenciam visibilidade e reputação de ambos os perfis
- Histórico de agendamentos acessível para ambos os perfis, com detalhes e avaliações associadas.
- Exibir avaliação média e número total de avaliações no perfil do instrutor para ajudar alunos na decisão de reserva.
- Permitir que instrutores vejam avaliações e comentários de alunos para melhorar seus serviços e reputação.
- Implementar moderação de avaliações para evitar abusos e garantir feedback construtivo. (Opcional para V1, pode ser considerado em versões futuras, considerar palavras-chave para moderação automática)

### RF07 — Histórico de Aulas

- Registro detalhado de todas as aulas realizadas (data, horário, local, conteúdo, avaliações)
- Disponível para aluno e instrutor em seus respectivos painéis
- Permite acompanhamento do progresso do aluno e histórico de serviços do instrutor
- Exibir detalhes de cada aula, incluindo avaliações e comentários, para ambos os perfis.
- Permitir exportação do histórico de aulas em formato PDF ou CSV para acompanhamento pessoal ou comprovação de experiência (Opcional para V1, pode ser considerado em versões futuras)

### RF08 — Dashboard do Instrutor

- Visualização de aulas agendadas e pendentes
- Métricas de desempenho (avaliação média, número de aulas realizadas)
- Gestão da própria agenda e disponibilidade
- Acesso a avaliações recebidas para melhoria contínua

### RF09 — Mensagens do Agendamento (assíncronas)

- Troca de mensagens assíncronas entre aluno e instrutor vinculada a um agendamento
- Histórico de mensagens acessível por ambas as partes
- Mensagens de Agendamento gerenciadas a partir de cada reserva, permitindo comunicação direta para esclarecimento de dúvidas, detalhes da aula e coordenação logística dentro da plataforma, sem necessidade de contato externo (ex.: WhatsApp) para manter rastreabilidade e segurança, modelo de "Fórum de Agendamento" onde cada reserva tem seu próprio espaço de mensagens, facilitando a organização e evitando confusões entre diferentes aulas.
- Notificações automáticas para novas mensagens relacionadas a um agendamento específico, garantindo que ambas as partes estejam cientes de atualizações e possam responder em tempo hábil, mesmo que a comunicação seja assíncrona.
- Definições de SLA para resposta a mensagens (ex.: resposta esperada em até 24 horas) para garantir um nível mínimo de comunicação e evitar frustrações, com possibilidade de alertas para mensagens não respondidas dentro do prazo.

### RF10 — Notificações

- Canais V1: E-mail
- Configuração de preferências de notificação para cada usuário (ex.: receber/notificar sobre novos agendamentos, lembretes, avaliações)
- Notificações automáticas para eventos relacionados a agendamentos e avaliações, garantindo que os usuários estejam sempre informados sobre o status de suas aulas, feedback recebido e outras interações importantes dentro da plataforma.
- Personalização de mensagens para cada tipo de evento, garantindo clareza e relevância das informações enviadas aos usuários, aumentando o engajamento e a satisfação com a plataforma. Exemplo: "Seu agendamento com [Nome do Instrutor] foi confirmado para [Data/Hora]. Prepare-se para sua aula!" ou "Você recebeu uma nova avaliação de [Nome do Aluno] após sua última aula. Confira seu feedback para melhorar seus serviços!".

### RF11 — Verificação de Credenciamento (Admin)

- Interface para upload de documentos pelo instrutor (credencial DETRAN, certidão negativa)
- Painel do admin para revisão e aprovação manual
- Instrutores não validados ficam invisíveis nos resultados de busca
- Storage de documentos serão feitos em AWS S3 (Free Tier) para evitar custos e complexidade de infraestrutura, com links seguros para acesso apenas pelo admin durante o processo de validação. Documentos serão excluídos após validação para minimizar riscos de segurança e privacidade.

> **Referência para validação manual:** lista de instrutores credenciados disponível em [gov.br](https://www.gov.br/transportes/pt-br/conteudos-cnh-do-brasil/por-dentro-da-nova-cnh-do-brasil) via painel Power BI, com filtros por estado, cidade e bairro.

---

## 4. Requisitos Não Funcionais (RNF)

| Código | Requisito |
|---|---|
| **RNF01** | **Stack:** Frontend em React(Vite, Tailwind CSS 4, ShadCN-ui, Leaflet) · Backend em Python (FastAPI, SQLAlchemy) · Banco de dados PostgreSQL + PostGIS para geolocalização |
| **RNF02** | **Performance:** Consultas de geolocalização (com PostGIS) devem retornar resultados em menos de 500ms |
| **RNF03** | **Segurança:** Criptografia de senhas (bcrypt), HTTPS obrigatório, conformidade com a LGPD |
| **RNF04** | **Responsividade:** Interface mobile-first, otimizada para uso em campo (aluno/instrutor em deslocamento) |
| **RNF05** | **Disponibilidade:** Mínimo de 99% de uptime para não interromper agendamentos ativos |
| **RNF06** | **Autenticação:** JWT com expiração configurável e renovação via refresh token |

---

## 5. Regras de Negócio (RN)

| Código | Regra |
|---|---|
| **RN01** | Apenas instrutores com credencial ativa e **validada manualmente pelo admin** aparecem nos resultados de busca. Validação feita via consulta ao painel Power BI do gov.br + análise de documentos enviados. |
| **RN02** | O sistema respeita a carga horária mínima de 2 horas estabelecida pela Resolução CONTRAN nº 1.020/2025, com SLOTS de 1h. Na V1, o agendamento só pode ser confirmado com duração total mínima de 2 horas (ex.: 2 slots consecutivos de 1 hora), com validação no frontend e no backend. |
| **RN03** | Um instrutor não pode ter dois agendamentos sobrepostos no mesmo intervalo de tempo. |
| **RN04** | Cancelamento das aulas sem penalidade podem ser feito em até 24 horas antes do horário agendado. Cancelamentos feitos com menos de 24 horas de antecedência podem resultar em penalidades para o aluno (ex.: bloqueio temporário de reservas por 7 dias) para incentivar o respeito à agenda dos instrutores e evitar cancelamentos de última hora que prejudicam a disponibilidade. |
| **RN05** | A avaliação mútua é liberada somente após a conclusão da aula (status: "realizada"). |
| **RN06** | Pagamentos são realizados diretamente entre aluno e instrutor, fora da plataforma. O sistema **não intermedia transações financeiras**. |
| **RN07** | O sistema de mensagens é assíncrono e vinculado a cada agendamento, sem suporte a chat em tempo real na V1. Priorizando interação em modelo de "Fórum" à cada agendamento. |

---

## 6. Decisões Arquiteturais

| Decisão | Justificativa |
|---|---|
| Sem sistema de pagamentos | Evitar responsabilidade legal. Funcionalidade premium pode ser considerada com produto maduro. |
| Validação DETRAN manual | APIs do DETRAN não são públicas. Validação manual pelo admin via Power BI (gov.br) é viável para o escopo acadêmico. |
| Mensagens assíncronas na V1 | Reduz complexidade técnica em relação a chat em tempo real e mantém rastreabilidade por agendamento. |
| Notificações V1 por e-mail | Evita custos e burocracia de APIs pagas (SMS/WhatsApp) e reduz risco de atraso no TCC. |
| Geolocalização com PostGIS | Busca geoespacial nativa e performática para atender RNF02 com crescimento da base. |
| Avaliação mútua | Impede que alunos problemáticos troquem de instrutor repetidamente sem deixar rastro. |
| Mobile-first | Público principal (alunos e instrutores) está em campo — o uso no celular é a regra, não a exceção. |
| Sem chat em tempo real | Foco em funcionalidades essenciais para V1, evitando complexidade técnica e riscos de atraso. |
| Sem histórico financeiro | Fora do escopo da V1, dado que pagamentos são feitos fora da plataforma. Pode ser considerado em versões futuras. |
|

---

## 7. Itens em Aberto

- [x] RF10: V1 definida com notificações por e-mail; demais canais ficam para versões futuras
- [x] Condutor habilitado tratado como subtipo de Aluno (campo no perfil, sem novo ator)
- [ ] Elaborar diagramas UML: casos de uso, classes, atividades, componentes, ER

---
