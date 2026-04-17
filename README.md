# LinkAuto - Conectando Alunos e Instrutores de Transito

O **LinkAuto** e uma plataforma web mobile-first para facilitar o agendamento
de aulas particulares de direcao entre alunos e instrutores autonomos
credenciados pelo DETRAN.

Este projeto foi desenvolvido como parte de um **Trabalho de Conclusao de Curso
(TCC)**.

## Funcionalidades Principais

### Para o Aluno

- **Busca Avancada:** pesquisa de instrutores por nome ou bairro.
- **Filtros Personalizados:** ordenacao por preco, avaliacao e proximidade.
- **Perfil do Instrutor:** visualizacao de credenciais validadas,
  especialidades e reputacao.
- **Agendamento Direto:** reserva em slots de 1h com duracao minima de 2h.
- **Mensagens de Agendamento:** comunicacao assincrona no modelo forum
  (sem chat em tempo real na V1).

### Para o Instrutor

- **Dashboard Operacional:** resumo de aulas realizadas, pendentes e
  desempenho.
- **Gestao de Solicitacoes:** aceite ou recusa de novos agendamentos com
  notificacao por e-mail.
- **Agenda Organizada:** lista de aulas confirmadas com detalhes do aluno.

### Guardrails da V1

- Sem intermediacao financeira: a plataforma nao processa pagamentos e nao
  exibe valores transacionados.
- Sem chat em tempo real: mensagens sao assincronas por agendamento.
- Avaliacao mutua liberada somente apos aula com status `REALIZADA`.
- Instrutor aparece na busca somente apos validacao do Admin.

## Tecnologias Utilizadas

- **Frontend:** React + Vite + Tailwind CSS 4 + ShadCN-ui + Leaflet
- **Backend:** Python + FastAPI + SQLAlchemy
- **Banco (dev):** SQLite3
- **Banco (prod):** PostgreSQL + PostGIS
- **Storage:** AWS S3 (documentos de credenciamento)
- **Email:** AWS SES
- **Auth:** JWT (access token curto) + refresh token

## Como Rodar o Projeto

Siga os passos abaixo para configurar o ambiente local.

### 1. Clonar o repositorio

```bash
git clone https://github.com/seu-usuario/linkauto.git
cd linkauto
```

### 2. Instalar as dependencias

Certifique-se de ter o Node.js instalado.

```bash
cd linkauto-frontend
npm install
```

### 3. Rodar a aplicacao

```bash
npm run dev
```
