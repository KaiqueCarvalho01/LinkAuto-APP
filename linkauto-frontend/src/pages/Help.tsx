import {
	Box,
	Container,
	Heading,
	Stack,
	Text,
} from "@chakra-ui/react";

const topics = [
	{
		title: "Como criar uma conta",
		text: "Acesse a página de cadastro, escolha o perfil Aluno ou Instrutor, informe e-mail e senha e confirme o login. Instrutores passam por validação manual antes de aparecerem na busca.",
	},
	{
		title: "Como agendar uma aula",
		text: "Faça login como aluno, busque instrutores na sua região, abra o perfil desejado e clique em “Agendar Aula”. O agendamento mínimo é de 2 horas, conforme a Resolução CONTRAN nº 1.020/2025.",
	},
	{
		title: "Como funciona o pagamento",
		text: "O pagamento é combinado e feito diretamente entre você e o instrutor, fora da plataforma. Acertem a forma de pagamento antes da aula.",
	},
	{
		title: "Cancelamentos",
		text: "Cancelamentos feitos com pelo menos 24 horas de antecedência não têm penalidade. Cancelamentos de última hora podem resultar em bloqueio temporário de novas reservas por 7 dias.",
	},
	{
		title: "Segurança e privacidade",
		text: "Todos os instrutores são validados manualmente pela nossa equipe. Seus dados pessoais são tratados em conformidade com a LGPD — veja mais na página de Privacidade.",
	},
	{
		title: "Sou instrutor: como começo?",
		text: "Crie sua conta como Instrutor, envie seus documentos (credencial DETRAN e certidão negativa), configure preço, região de atuação e agenda. Após a aprovação, seu perfil fica visível para os alunos.",
	},
];

export default function Help() {
	return (
		<Stack gap={0} bg="bg.canvas">
			<Box
				py={20}
				bg="surface.panel"
				borderBottom="1px solid"
				borderColor="border.subtle">
				<Container maxW="container.lg">
					<Stack gap={4}>
						<Heading fontSize={{ base: "3xl", md: "4xl" }} fontWeight="800">
							Central de Ajuda
						</Heading>
						<Text fontSize="lg" color="text.muted" maxW="720px">
							Respostas rápidas para as dúvidas mais comuns de alunos e
							instrutores.
						</Text>
					</Stack>
				</Container>
			</Box>

			<Box py={16}>
				<Container maxW="container.lg">
					<Stack gap={8} maxW="720px">
						{topics.map((topic) => (
							<Stack
								key={topic.title}
								gap={2}
								p={6}
								bg="surface.panel"
								border="1px solid"
								borderColor="border.subtle"
								borderRadius="2xl">
								<Heading fontSize="lg" fontWeight="700">
									{topic.title}
								</Heading>
								<Text color="text.muted" fontSize="sm" lineHeight="tall">
									{topic.text}
								</Text>
							</Stack>
						))}
					</Stack>
				</Container>
			</Box>
		</Stack>
	);
}
