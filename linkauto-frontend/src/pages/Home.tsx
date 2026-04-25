import { ArrowRight, Compass, ShieldCheck, TimerReset } from "lucide-react";
import {
	Box,
	Button,
	Container,
	Grid,
	Heading,
	HStack,
	SimpleGrid,
	Stack,
	Text,
	Badge,
	Circle,
} from "@chakra-ui/react";
import { useState, useMemo } from "react";
import { InstructorMap } from "../components/InstructorMap";
import { getMockInstructors } from "../services/mockData";

interface HomeProps {
	readonly isAuthenticated: boolean;
	readonly onOpenLogin: () => void;
	readonly onOpenSearch: () => void;
}

const highlights = [
	{
		title: "Busca Geolocalizada",
		description:
			"Encontre instrutores credenciados por bairro, distância e especialidade.",
		icon: Compass,
		color: "brand.500",
	},
	{
		title: "Governança de Perfis",
		description:
			"Fluxo de aprovação administrativa para garantir qualidade e segurança.",
		icon: ShieldCheck,
		color: "laGreen.600",
	},
	{
		title: "Regras de Agenda",
		description:
			"Agendamentos de 2h e linha do tempo de status para total previsibilidade.",
		icon: TimerReset,
		color: "laBlue.600",
	},
];

export default function Home({
	isAuthenticated,
	onOpenLogin,
	onOpenSearch,
}: HomeProps) {
	const [selectedId, setSelectedId] = useState<string | undefined>();
	const instructors = useMemo(() => getMockInstructors(), []);

	return (
		<Stack minH="100vh" gap={0} bg="bg.canvas">
			{/* Hero Section */}
			<Box
				position="relative"
				overflow="hidden"
				pt={{ base: 12, md: 24 }}
				pb={{ base: 16, md: 32 }}
				bgGradient="to-b"
				gradientFrom="surface.panel"
				gradientTo="bg.canvas">
				{/* Background Decoration */}
				<Box
					position="absolute"
					top="-10%"
					right="-5%"
					w="600px"
					h="600px"
					bg="brand.500"
					filter="blur(120px)"
					opacity="0.05"
					borderRadius="full"
					zIndex={0}
				/>

				<Container maxW="container.xl" position="relative" zIndex={1}>
					<Grid
						templateColumns={{ base: "1fr", lg: "1fr 1fr" }}
						gap={{ base: 12, lg: 16 }}
						alignItems="center">
						<Stack gap={8}>
							<Stack gap={4}>
								<Badge
									alignSelf="start"
									variant="subtle"
									colorPalette="brand"
									px={3}
									py={1}
									rounded="full"
									textTransform="none"
									fontWeight="bold">
									LinkAuto MVP
								</Badge>
								<Heading
									fontSize={{
										base: "4xl",
										md: "5xl",
										lg: "6xl",
									}}
									lineHeight="1.1"
									color="text.primary"
									fontWeight="800"
									letterSpacing="tight">
									A liberdade de dirigir começa com a{" "}
									<Text as="span" color="brand.500">
										conexão certa.
									</Text>
								</Heading>
								<Text
									fontSize={{ base: "lg", md: "xl" }}
									lineHeight="1.6"
									color="text.muted"
									maxW="540px">
									Encontre instrutores validados, agende aulas
									em segundos e acompanhe sua evolução em uma
									plataforma segura e moderna.
								</Text>
							</Stack>

							<HStack gap={4} flexWrap="wrap">
								<Button
									size="xl"
									px={10}
									colorPalette="brand"
									rounded="full"
									fontWeight="bold"
									onClick={
										isAuthenticated
											? onOpenSearch
											: onOpenLogin
									}
									boxShadow="0 10px 20px -5px var(--colors-brand-500)">
									{isAuthenticated
										? "Encontrar Instrutores"
										: "Acessar Plataforma"}
									<ArrowRight size={20} />
								</Button>
								<Button
									size="xl"
									variant="outline"
									px={8}
									rounded="full"
									borderColor="border.emphasized"
									_hover={{
										fill: "white",
										bg: "border.emphasized",
									}}
									onClick={onOpenSearch}>
									Ver Busca Demo
								</Button>
							</HStack>

							<HStack gap={6} pt={4}>
								<HStack gap={2}>
									<Circle size={2} bg="laGreen.500" />
									<Text fontSize="sm" fontWeight="bold">
										Instrutores Verificados
									</Text>
								</HStack>
								<HStack gap={2}>
									<Circle size={2} bg="laBlue.500" />
									<Text fontSize="sm" fontWeight="bold">
										Suporte 24h
									</Text>
								</HStack>
							</HStack>
						</Stack>

						<Box
							h={{ base: "400px", lg: "600px" }}
							position="relative"
							borderRadius="3xl"
							overflow="hidden"
							boxShadow="0 32px 64px -16px rgba(0,0,0,0.12)"
							border="8px solid"
							borderColor="surface.panel">
							<InstructorMap
								instructors={instructors}
								selectedInstructorId={selectedId}
								onSelect={(id) => setSelectedId(id)}
								onBook={() => {
									// In V1, this might redirect to lesson details or search
									onOpenSearch();
								}}
							/>

							{/* Floating Overlay for Map Interaction Hint */}
						</Box>
					</Grid>
				</Container>
			</Box>
			{/* Highlights Section */}
			<Box py={24} bg="bg.muted">
				<Container maxW="container.xl">
					<Stack gap={16}>
						<Stack
							textAlign="center"
							gap={4}
							maxW="700px"
							mx="auto">
							<Heading fontSize="3xl" fontWeight="800">
								Feito para transformar sua experiência
							</Heading>
							<Text color="text.muted" fontSize="lg">
								Eliminamos a burocracia e a incerteza do
								processo de habilitação, trazendo transparência
								e tecnologia para o dia a dia.
							</Text>
						</Stack>

						<SimpleGrid columns={{ base: 1, md: 3 }} gap={8}>
							{highlights.map((item) => {
								const Icon = item.icon;
								return (
									<Box
										key={item.title}
										bg="surface.panel"
										p={8}
										borderRadius="2xl"
										border="1px solid"
										borderColor="border.subtle"
										transition="all 0.3s"
										_hover={{
											transform: "translateY(-8px)",
											boxShadow:
												"0 20px 40px -12px rgba(0,0,0,0.08)",
											borderColor: "brand.200",
										}}>
										<Stack gap={6}>
											<Box
												w="56px"
												h="56px"
												borderRadius="xl"
												display="grid"
												placeItems="center"
												bg="brand.50"
												color={item.color}>
												<Icon size={28} />
											</Box>
											<Stack gap={2}>
												<Text
													fontSize="xl"
													fontWeight="800"
													color="text.primary">
													{item.title}
												</Text>
												<Text
													color="text.muted"
													lineHeight="tall">
													{item.description}
												</Text>
											</Stack>
										</Stack>
									</Box>
								);
							})}
						</SimpleGrid>
					</Stack>
				</Container>
			</Box>
			{/* Identity Box */}
			{/* Reasons to use Box  */}
			{/*  Funcionalities Box */}
			{/*  Testimonials Marquee Grid BOX */}
			{/*   Mini FAQ BOX */}
		</Stack>
	);
}
