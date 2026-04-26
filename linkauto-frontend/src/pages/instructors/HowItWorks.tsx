import {
	Box,
	Container,
	Heading,
	SimpleGrid,
	Stack,
	Text,
	Circle,
	AccordionRoot,
	AccordionItem,
	AccordionItemTrigger,
	AccordionItemContent,
	AccordionItemIndicator,
} from "@chakra-ui/react";
import { UserPlus, Settings, BellRing, BadgeDollarSign } from "lucide-react";

export default function HowItWorks() {
	const steps = [
		{
			title: "1. Cadastro e Validação",
			description: "Envie seus documentos (CNH e Credencial) para nossa curadoria. Segurança é a nossa base.",
			icon: UserPlus,
		},
		{
			title: "2. Configure sua Agenda",
			description: "Defina os horários que deseja trabalhar e as regiões que atende. Flexibilidade total.",
			icon: Settings,
		},
		{
			title: "3. Receba Alunos",
			description: "Seja notificado quando um novo aluno agendar uma aula. Gerencie tudo pelo app.",
			icon: BellRing,
		},
		{
			title: "4. Pagamento Direto",
			description: "O valor da aula cai na sua conta LinkAuto assim que a aula é concluída.",
			icon: BadgeDollarSign,
		},
	];

	const faqItems = [
		{
			value: "gas",
			title: "Quem paga o combustível?",
			text: "Como instrutor autônomo, os custos operacionais (gasolina, manutenção, seguro) são de sua responsabilidade, mas você compensa isso cobrando um valor justo pela hora/aula.",
		},
		{
			value: "car",
			title: "Posso usar carro de aluguel?",
			text: "Sim, desde que o veículo esteja segurado e atenda aos requisitos mínimos de segurança e conforto exigidos pela plataforma.",
		},
		{
			value: "repasse",
			title: "Como funciona o repasse?",
			text: "Os pagamentos são processados pela plataforma e o repasse para sua conta bancária ocorre semanalmente, de forma automática.",
		},
		{
			value: "detran",
			title: "Preciso ser credenciado no Detran?",
			text: "Para dar aulas de primeira habilitação, sim. Para aulas de reciclagem ou perder o medo para habilitados, as exigências podem variar conforme a legislação local.",
		},
	];

	return (
		<Stack gap={0} bg="bg.canvas">
			{/* Hero Section */}
			<Box py={24} bg="surface.panel" borderBottom="1px solid" borderColor="border.subtle">
				<Container maxW="container.lg">
					<Stack gap={6} textAlign="center" align="center">
						<Heading
							fontSize={{ base: "4xl", md: "5xl" }}
							fontWeight="800"
							letterSpacing="tight">
							Seu novo escritório é o seu próprio carro.
						</Heading>
						<Text fontSize="lg" color="text.muted" maxW="600px">
							A LinkAuto fornece as ferramentas tecnológicas para você gerenciar 
							sua carreira autônoma com profissionalismo e escala.
						</Text>
					</Stack>
				</Container>
			</Box>

			{/* Steps Section */}
			<Box py={24}>
				<Container maxW="container.xl">
					<SimpleGrid columns={{ base: 1, sm: 2, lg: 4 }} gap={12}>
						{steps.map((step) => (
							<Stack key={step.title} gap={6} align="center" textAlign="center" p={6} borderRadius="2xl" transition="background 0.2s" _hover={{ bg: "surface.muted" }}>
								<Circle size={16} bg="laBlue.50" color="laBlue.500">
									<step.icon size={32} />
								</Circle>
								<Stack gap={2}>
									<Text fontSize="xl" fontWeight="800">{step.title}</Text>
									<Text color="text.muted" fontSize="sm">{step.description}</Text>
								</Stack>
							</Stack>
						))}
					</SimpleGrid>
				</Container>
			</Box>

			{/* FAQ Section */}
			<Box py={24} bg="bg.muted">
				<Container maxW="container.md">
					<Stack gap={12}>
						<Heading textAlign="center" fontSize="3xl" fontWeight="800">Perguntas Frequentes</Heading>
						<AccordionRoot collapsible variant="subtle">
							{faqItems.map((item) => (
								<AccordionItem key={item.value} value={item.value} py={2} bg="surface.panel" px={6} borderRadius="xl" mb={4} border="1px solid" borderColor="border.subtle">
									<AccordionItemTrigger fontWeight="bold">
										{item.title}
										<AccordionItemIndicator />
									</AccordionItemTrigger>
									<AccordionItemContent color="text.muted" pt={2} pb={4}>
										{item.text}
									</AccordionItemContent>
								</AccordionItem>
							))}
						</AccordionRoot>
					</Stack>
				</Container>
			</Box>
		</Stack>
	);
}
