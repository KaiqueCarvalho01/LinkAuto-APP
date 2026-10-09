import {
	Box,
	Container,
	Heading,
	Stack,
	Text,
} from "@chakra-ui/react";

const sections = [
	{
		title: "1. Dados que tratamos",
		text: "Coletamos apenas os dados necessários para intermediar as aulas: nome, e-mail, telefone, cidade, tipo de habilitação, localização para busca geolocalizada e, para instrutores, os documentos de credenciamento enviados para validação.",
	},
	{
		title: "2. Bases legais",
		text: "O agendamento se apoia na execução de contrato (art. 7º, V da LGPD). A guarda e a validação dos documentos do instrutor cumprem obrigação legal (art. 7º, II), exigida pela Resolução CONTRAN nº 1.020/2025. O sistema de avaliações se fundamenta no legítimo interesse do controlador (art. 7º, IX), com medidas de transparência e proporcionalidade.",
	},
	{
		title: "3. Documentos de instrutores",
		text: "Credencial DETRAN e certidão negativa são armazenados com acesso restrito à equipe de moderação e excluídos após a validação do cadastro, minimizando riscos de privacidade.",
	},
	{
		title: "4. Compartilhamento",
		text: "Seus dados não são vendidos. São compartilhados apenas com a contraparte do agendamento (aluno e instrutor) no estritamente necessário para a realização da aula.",
	},
	{
		title: "5. Seus direitos",
		text: "Nos termos da LGPD, você pode solicitar acesso, correção, portabilidade ou exclusão dos seus dados pessoais a qualquer momento pelo e-mail privacidade@linkauto.com.br.",
	},
	{
		title: "6. Segurança",
		text: "Utilizamos criptografia de senhas (bcrypt), autenticação por token (JWT) e HTTPS para proteger as informações trafegadas na plataforma.",
	},
];

export default function Privacy() {
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
							Privacidade e LGPD
						</Heading>
						<Text fontSize="lg" color="text.muted" maxW="720px">
							Como a LinkAuto trata seus dados pessoais, em conformidade com
							a Lei nº 13.709/2018 (LGPD).
						</Text>
					</Stack>
				</Container>
			</Box>

			<Box py={16}>
				<Container maxW="container.lg">
					<Stack gap={8} maxW="720px">
						{sections.map((section) => (
							<Stack key={section.title} gap={2}>
								<Heading fontSize="lg" fontWeight="700">
									{section.title}
								</Heading>
								<Text color="text.muted" fontSize="sm" lineHeight="tall">
									{section.text}
								</Text>
							</Stack>
						))}
					</Stack>
				</Container>
			</Box>
		</Stack>
	);
}
