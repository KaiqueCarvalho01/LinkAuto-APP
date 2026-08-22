# Problemas identificados

, 

2. Foi identificado que ao agendar uma aula, o instutor não possui a opção de confirmá-la. Exemplo: "aluno" marcou aula com "Camila Rocha" (pré-seeded), mas a instrutora não possui a opção de confirmar a aula, apenas de recusar. Mesmo sem o cron job de notificação de aulas o instrutor deve ter a opção de confirmar a aula solicitada.

3. Devemos impedir que instrutor ou aluno possam agendar aulas com ele mesmo. Por exemplo, o instrutor "Camila Rocha" não pode agendar aula com ela mesma, assim como o aluno "João Silva" não pode agendar aula com ele mesmo. Isso deve ser validado no backend para impedir que seja possível violar a regra. No frontend o botão de agendamento deve ser desabilitado caso o usuário logado seja o mesmo do perfil que está sendo visualizado. É também fundamental para impedir que o usuário manipule suas avaliações dentro da plataforma.

4. Impedir que quando logado com ROLE "instrutor" o mesmo não possa executar agendamento de aulas. Considerando que o instrutor pode acessar seu perfil multi-role como ALUNO para fazer agendamentos adequadamente dentro da plataforma.

5. Gatilho Autônomo de Cron Jobs: Os endpoints /api/v1/jobs/* (timeout de reservas, conclusão automática e lembretes 24h) necessitam de configuração em produção via AWS EventBridge Scheduler, Celery Beat ou cron do Linux no container.  

6. Expurgo Automático de Documentos (AWS S3): Implementar rotina de expurgo programado (Lifecycle Rule no bucket S3 ou job de limpeza) para deletar os arquivos de CNH/certidões após aprovação administrativa, garantindo conformidade com a LGPD e o RF11.

7. Como ainda não houveram aulas "realizadas" na plataforma, não é possível validar o fluxo de avaliação de instrutores e alunos. É necessário criar um script de seed para popular a base de dados com aulas concluídas, permitindo que o fluxo de avaliação seja testado e validado. Podemos considerar 2 cenários: (i) aulas concluídas com avaliações e (ii) aulas concluídas sem avaliações, para validar o fluxo completo de avaliação e notificações. Como os e-mails "@linkauto.com.br" não são válidos, podemos utilizar como teste a integração do AWS SES SOMENTE quando validado o fluxo de avaliação, para não gerar e-mails inválidos durante os testes, antes disso podemos definir outros critérios de teste para validação do fluxo de avaliação, como logs no console ou mock de envio de e-mails.

8. Integração CI/CD com Smoke Tests: Expandir a suíte do Playwright (student-booking-smoke.spec.ts) no pipeline de GitHub Actions para execução de testes end-to-end automatizados a cada pull request. (Validar se existe suíte de testes automatizados. Caso contrário, devemos levantar as necessidades para uso correto do playwright).