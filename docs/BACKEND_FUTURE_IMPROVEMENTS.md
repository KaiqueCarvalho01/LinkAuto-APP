# Backend Future Improvements & Backlog V2 (LinkAuto)

> **Status**: Documento de Planejamento Estratégico (YAGNI / Backlog de Evolução)
> **Objetivo**: Registrar soluções avaliadas e explicitamente postergadas na Phase 6 (Polish & Hardening) para evitar carga cognitiva adicional em V1, definindo prós e contras estruturados para a equipe de engenharia/proprietários do projeto.

---

## 1. Denylist de Refresh Tokens (Server-Side)

### Contexto
Atualmente, a revogação de tokens JWT em caso de logout ou comprometimento imediato é parcial. Os Refresh Tokens são rotacionados a cada requisição, mas não há um store server-side para invalidar tokens ativos antes do vencimento natural.

### Solução Proposta para V2
Implementar um mecanismo de revogação imediata (Denylist) usando Redis.

### Análise de Prós e Contras

| Prós (Benefícios) | Contras (Custos / Complexidade) |
| :--- | :--- |
| **Segurança Máxima**: Permite revogar instantaneamente qualquer sessão ativa em caso de logout ou detecção de invasão (OWASP API02). | **Carga Cognitiva e Ops**: Adiciona o Redis como dependência obrigatória de infraestrutura (aumentando custos de hospedagem e complexidade de deploy). |
| **Conformidade (Compliance)**: Facilita auditorias de segurança de nível corporativo e conformidade regulatória. | **Ponto Único de Falha**: Se o Redis ficar offline, as rotas de autenticação/autorização podem falhar (requer fallback robusto). |
| **Simplicidade no App**: Gerenciamento de TTL automático pelo Redis (usando comandos `EXPIRE` do próprio banco). | **Latência adicional**: Cada validação de token passa a exigir uma consulta em cache (minimizada por ser Redis, mas existente). |

### Decisão Final (V1)
**Adiada (YAGNI)**. O LinkAuto V1 roda em modelo single-instance e a rotação contínua de refresh tokens implementada já oferece proteção robusta contra replay-attacks para esta fase MVP do produto.

---

## 2. Rate Limiting Distribuído (Redis-backed)

### Contexto
O rate limiting introduzido na Phase 6 usa `slowapi` com armazenamento em memória (`MemoryBackend`). Isso significa que cada réplica da aplicação rastreia o limite de requisições de forma isolada.

### Solução Proposta para V2
Migrar o backend do `slowapi` do `MemoryBackend` para o `RedisBackend`.

### Análise de Prós e Contras

| Prós (Benefícios) | Contras (Custos / Complexidade) |
| :--- | :--- |
| **Limitação Consistente**: Em produção real com múltiplas instâncias atrás de um Load Balancer, o limite de requisições por IP é unificado globalmente. | **Complexidade Local**: Para desenvolvedores locais, passa a ser necessário subir uma instância do Redis (via Docker) para testar o fluxo. |
| **Resiliência a Ataques Coordenados**: Impede bypass de rate limit ao rotacionar conexões entre diferentes instâncias da API. | **Sobrecarga de Conexões**: Requer configuração adequada de pooling de conexões no Redis para aguentar rajadas de tráfego. |

### Decisão Final (V1)
**Adiada (YAGNI)**. O rate limit global e por IP em memória atende com folga o tráfego esperado para V1, que opera em infraestrutura enxuta. Os limites propostos (ex: login=10/min, register=5/min) foram documentados e validados pelo usuário para os propósitos de desenvolvimento.

---

## 3. Sandboxing / Escaneamento de Vírus em Upload de Arquivos

### Contexto
O LinkAuto permite que instrutores enviem documentos de credenciamento (PDF/Imagens). Na Phase 6, blindamos o upload contra extensão falsa usando verificação rigorosa de **Magic Bytes**. 

### Solução Proposta para V2
Integrar um serviço ou ferramenta de terceiros para escaneamento de malware no upload (ex: ClamAV, AWS GuardDuty para S3 ou APIs SaaS como Cloudmersive).

### Análise de Prós e Contras

| Prós (Benefícios) | Contras (Custos / Complexidade) |
| :--- | :--- |
| **Segurança de Infraestrutura**: Garante que arquivos maliciosos nunca cheguem aos administradores humanos durante a revisão do Detran. | **Custo Financeiro e Latência**: Escaneamento por API adiciona custo recorrente. Escaneamento local via ClamAV consome muita CPU/Memória na máquina. |
| **Reputação de Rede**: Evita que o bucket S3 do projeto seja sinalizado como provedor de arquivos de phishing ou malware. | **Complexidade de Integração**: Requer fila de mensageria assíncrona (Celery/SQS), pois o escaneamento em tempo real atrasa a experiência do usuário. |

### Decisão Final (V1)
**Adiada (YAGNI)**. A combinação de **MIME whitelist estrita** + **verificação de Magic Bytes determinística** impede 99% das tentativas de abuso comuns (como upload de scripts shell disfarçados de imagem). O isolamento dos arquivos no S3 e exclusão obrigatória pelo admin mitigam o risco em V1.

---

## 4. Fluxo Completo de Password Reset

### Contexto
Atualmente, o reset de senha é simulado, retornando um status `202 Accepted` de placeholder, conforme o escopo da V1.

### Solução Proposta para V2
Implementar fluxo completo com geração de tokens criptográficos expiráveis de uso único, persistência em tabela dedicada ou cache temporário, e integração real com gateway de e-mail (AWS SES).

### Análise de Prós e Contras

| Prós (Benefícios) | Contras (Custos / Complexidade) |
| :--- | :--- |
| **Autonomia do Usuário**: Permite que alunos e instrutores recuperem o acesso às contas sem necessidade de suporte manual dos administradores. | **Superfície de Ataque de Segurança**: Fluxos de reset de senha são alvos comuns para Account Takeover (requer tokens criptográficos seguros, expiração curta e proteção de enumeração de usuário). |

### Decisão Final (V1)
**Adiada**. O endpoint retorna 202 com segurança e auditoria (log estruturado), suficiente para o fluxo do MVP.
