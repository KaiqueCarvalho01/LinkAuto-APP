import {
	Box,
	Container,
	Heading,
	SimpleGrid,
	Stack,
	Text,
} from "@chakra-ui/react";
import { Search, CalendarDays, Star, ShieldCheck } from "lucide-react";

const highlights = [
	{
		icon: Search,
		title: "Busca geolocalizada",
		description:
			"Encontre instrutores credenciados próximos de você, com filtros por preço, avaliação e especialidade.",
	},
	{
		icon: CalendarDays,
		title: "Agendamento simples",
		description:
			"Consulte a agenda disponível e reserve suas aulas práticas com poucos toques, pelo celular ou computador.",
	},
	{
		icon: Star,
		title: "Avaliação mútua",
		description:
			"Alunos e instrutores se avaliam após cada aula, criando reputação transparente para toda a comunidade.",
	},
	{
		icon: ShieldCheck,
		title: "Instrutores validados",
		description:
			"Cada instrutor passa por verificação manual de credencial DETRAN e antecedentes antes de aparecer na busca.",
	},
];

export default function About() {
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
							Sobre o LinkAuto
						</Heading>
						<Text fontSize="lg" color="text.muted" maxW="720px">
							O LinkAuto é uma plataforma de agendamento que conecta
							candidatos à CNH e condutores habilitados a instrutores de
							trânsito autônomos credenciados pelo DETRAN.
						</Text>
					</Stack>
				</Container>
			</Box>

			<Box py={16}>
				<Container maxW="container.lg">
					<Stack gap={10} maxW="720px">
						<Stack gap={3}>
							<Heading fontSize="2xl" fontWeight="700">
								O porquê do LinkAuto
							</Heading>
							<Text color="text.muted" fontSize="md" lineHeight="tall">
								A Resolução CONTRAN nº 1.020/2025 permitiu que instrutores
								credenciados ministrem aulas práticas de forma autônoma, fora
								das autoescolas. Essa liberdade, porém, deixou os alunos sem
								um canal confiável para encontrar, comparar e agendar esses
								profissionais. O LinkAuto preenche exatamente essa lacuna.
							</Text>
						</Stack>

						<Stack gap={3}>
							<Heading fontSize="2xl" fontWeight="700">
								Nosso compromisso
							</Heading>
							<Text color="text.muted" fontSize="md" lineHeight="tall">
								Validamos manualmente cada instrutor, protegemos seus dados
								pessoais em conformidade com a LGPD e mantemos a comunicação
								e o agendamento dentro da plataforma, com rastreabilidade e
								transparência. O pagamento é sempre combinado diretamente
								entre aluno e instrutor — a LinkAuto não intermedia valores.
							</Text>
						</Stack>
					</Stack>
				</Container>
			</Box>

			<Box py={16} bg="bg.muted">
				<Container maxW="container.xl">
					<SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} gap={8}>
						{highlights.map((item) => (
							<Stack key={item.title} gap={4}>
								<item.icon size={28} color="var(--chakra-colors-brand-500)" />
								<Heading fontSize="lg" fontWeight="700">
									{item.title}
								</Heading>
								<Text color="text.muted" fontSize="sm" lineHeight="tall">
									{item.description}
								</Text>
							</Stack>
						))}
					</SimpleGrid>
				</Container>
			</Box>

			<Box py={16}>
				<Container maxW="container.lg">
					<Stack gap={3} maxW="720px">
						<Heading fontSize="2xl" fontWeight="700">
							Projeto acadêmico
						</Heading>
						<Text color="text.muted" fontSize="md" lineHeight="tall">
							O LinkAuto é desenvolvido como projeto de Trabalho de Conclusão
							de Curso (TCC) do curso de Análise e Desenvolvimento de Sistemas
							da Fatec de Mogi Mirim, em 2026. A plataforma é gratuita e de
							uso acadêmico.
						</Text>
					</Stack>
				</Container>
			</Box>
		</Stack>
	);
}
