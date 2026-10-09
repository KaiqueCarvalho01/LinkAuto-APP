import {
	Box,
	Container,
	Heading,
	Stack,
	Text,
} from "@chakra-ui/react";

const sections = [
	{
		title: "1. Objeto",
		text: "Estes Termos de Uso regulam o acesso e a utilização da plataforma LinkAuto, que conecta alunos a instrutores de trânsito autônomos credenciados pelo DETRAN. Ao criar uma conta, você concorda com estas condições.",
	},
	{
		title: "2. Contas e perfis",
		text: "Alunos e instrutores devem fornecer informações verdadeiras. O cadastro de instrutor exige validação manual dos documentos enviados (credencial DETRAN e certidão negativa de antecedentes) antes que o perfil seja exibido nos resultados de busca.",
	},
	{
		title: "3. Pagamentos",
		text: "A LinkAuto não intermedia transações financeiras. O valor, a forma e o momento do pagamento são combinados diretamente entre aluno e instrutor, fora da plataforma.",
	},
	{
		title: "4. Agendamentos e cancelamentos",
		text: "O agendamento mínimo é de 2 horas, conforme a Resolução CONTRAN nº 1.020/2025. Cancelamentos sem penalidade podem ser feitos com pelo menos 24 horas de antecedência; cancelamentos de última hora podem acarretar bloqueio temporário de novas reservas por 7 dias.",
	},
	{
		title: "5. Conduta e avaliações",
		text: "Alunos e instrutores se avaliam mutuamente após cada aula realizada. Avaliações ofensivas, discriminatórias ou fraudulentas podem ser removidas pela moderação da plataforma.",
	},
	{
		title: "6. Responsabilidade",
		text: "A LinkAuto atua como intermediadora tecnológica. Instrutores são responsáveis pelo serviço prestado, pelo veículo utilizado e pelo cumprimento da legislação de trânsito vigente.",
	},
	{
		title: "7. Contato",
		text: "Dúvidas sobre estes termos podem ser enviadas para contato@linkauto.com.br.",
	},
];

export default function Terms() {
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
							Termos de Uso
						</Heading>
						<Text fontSize="lg" color="text.muted" maxW="720px">
							Última atualização: outubro de 2026.
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
