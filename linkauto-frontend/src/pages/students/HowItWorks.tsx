import {
	Box,
	Container,
	Heading,
	SimpleGrid,
	Stack,
	Text,
	Circle,
	Icon,
	AccordionRoot,
	AccordionItem,
	AccordionItemTrigger,
	AccordionItemContent,
	AccordionItemIndicator,
	Separator,
} from "@chakra-ui/react";
import { Search, CalendarDays, Car, Wallet, FileCheck } from "lucide-react";

export default function HowItWorks() {
	const steps = [
		{
			title: "1. Busque",
			description:
				"Filtre instrutores por localização, preço, categoria e avaliações de outros alunos.",
			icon: Search,
		},
		{
			title: "2. Agende",
			description:
				"Escolha um horário livre na agenda do instrutor e pague com segurança via PIX ou Cartão.",
			icon: CalendarDays,
		},
		{
			title: "3. Dirija",
			description:
				"Encontre seu instrutor no local marcado e comece sua aula. Sua evolução é registrada no app.",
			icon: Car,
		},
	];

	const faqItems = [
		{
			value: "detran",
			title: "Preciso ter o laudo do DETRAN aberto?",
			text: "Para aulas de primeira habilitação, sim. Você deve estar com o processo ativo no DETRAN. Para habilitados, basta sua CNH válida.",
		},
		{
			value: "payment",
			title: "Como funciona o pagamento?",
			text: "Você paga por aula ou pacotes diretamente na plataforma. O dinheiro fica protegido e só é repassado ao instrutor após a aula ser realizada.",
		},
		{
			value: "cancel",
			title: "Posso cancelar uma aula agendada?",
			text: "Sim. Cancelamentos com mais de 24h de antecedência possuem reembolso total. Regras específicas podem variar por instrutor.",
		},
	];

	return (
		<Stack gap={0} bg="bg.canvas">
			{/* Hero Section */}
			<Box
				py={24}
				bg="surface.panel"
				borderBottom="1px solid"
				borderColor="border.subtle">
				<Container maxW="container.lg">
					<Stack gap={6} textAlign="center" align="center">
						<Heading
							fontSize={{ base: "4xl", md: "5xl" }}
							fontWeight="800"
							letterSpacing="tight">
							O Caminho para a Autonomia.
						</Heading>
						<Text fontSize="lg" color="text.muted" maxW="600px">
							A LinkAuto conecta você diretamente aos melhores
							profissionais, eliminando intermediários e focando
							no seu aprendizado.
						</Text>
					</Stack>
				</Container>
			</Box>

			{/* Steps Section */}
			<Box py={24}>
				<Container maxW="container.xl">
					<SimpleGrid columns={{ base: 1, md: 3 }} gap={12}>
						{steps.map((step) => (
							<Stack
								key={step.title}
								gap={6}
								align="center"
								textAlign="center">
								<Circle
									size={20}
									bg="brand.50"
									color="brand.500">
									<step.icon size={36} />
								</Circle>
								<Stack gap={2}>
									<Text fontSize="2xl" fontWeight="800">
										{step.title}
									</Text>
									<Text color="text.muted" fontSize="md">
										{step.description}
									</Text>
								</Stack>
							</Stack>
						))}
					</SimpleGrid>
				</Container>
			</Box>

			{/* Pricing Section */}
			<Box py={24} bg="bg.muted">
				<Container maxW="container.xl">
					<SimpleGrid
						columns={{ base: 1, lg: 2 }}
						gap={16}
						alignItems="center">
						<Stack gap={8}>
							<Heading fontSize="3xl" fontWeight="800">
								Custos e Transparência
							</Heading>
							<Text fontSize="lg" color="text.muted">
								No modelo tradicional, você paga taxas
								administrativas altas. Na LinkAuto, a maior
								parte do valor vai direto para quem te ensina.
							</Text>
							<SimpleGrid columns={2} gap={6}>
								<PricingFactor
									icon={Wallet}
									title="Preço Justo"
									desc="Aulas a partir de R$ 80,00"
								/>
								<PricingFactor
									icon={FileCheck}
									title="Sem Taxas Ocultas"
									desc="Você vê o valor total antes de pagar"
								/>
							</SimpleGrid>
						</Stack>
						<Box
							bg="surface.panel"
							p={10}
							borderRadius="3xl"
							border="1px solid"
							borderColor="border.warning">
							<Stack gap={6}>
								<Text fontWeight="bold">
									Composição do Preço:
								</Text>
								<PriceRow
									label="Hora/Aula Instrutor"
									value="R$ 80,00"
								/>
								<PriceRow
									label="Usar a melhor plataforma do Brasil"
									value="R$ 0,00"
								/>
								<Separator />
								<PriceRow
									label="Total por Aula"
									value="R$ 80,00"
									isBold
								/>
							</Stack>
						</Box>
					</SimpleGrid>
				</Container>
			</Box>

			{/* FAQ Section */}
			<Box py={24}>
				<Container maxW="container.md">
					<Stack gap={12}>
						<Heading
							textAlign="center"
							fontSize="3xl"
							fontWeight="800">
							Dúvidas Frequentes de Alunos
						</Heading>
						<AccordionRoot collapsible variant="subtle">
							{faqItems.map((item) => (
								<AccordionItem
									key={item.value}
									value={item.value}
									py={2}>
									<AccordionItemTrigger fontWeight="bold">
										{item.title}
										<AccordionItemIndicator />
									</AccordionItemTrigger>
									<AccordionItemContent color="text.muted">
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

function PricingFactor({
	icon: LucideIcon,
	title,
	desc,
}: {
	icon: React.ElementType;
	title: string;
	desc: string;
}) {
	return (
		<Stack gap={3}>
			<Icon as={LucideIcon} color="brand.500" w={6} h={6} />
			<Box>
				<Text fontWeight="bold">{title}</Text>
				<Text fontSize="sm" color="text.muted">
					{desc}
				</Text>
			</Box>
		</Stack>
	);
}

function PriceRow({
	label,
	value,
	isBold = false,
}: {
	label: string;
	value: string;
	isBold?: boolean;
}) {
	return (
		<Box display="flex" justifyContent="space-between">
			<Text fontWeight={isBold ? "bold" : "normal"}>{label}</Text>
			<Text
				fontWeight={isBold ? "bold" : "normal"}
				color={isBold ? "brand.500" : "text.primary"}>
				{value}
			</Text>
		</Box>
	);
}
