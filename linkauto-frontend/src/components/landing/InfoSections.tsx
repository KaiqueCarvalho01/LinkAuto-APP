import {
	Box,
	Container,
	Heading,
	SimpleGrid,
	Stack,
	Text,
	Circle,
	Icon,
	Button,
} from "@chakra-ui/react";
import {
	Search,
	Calendar,
	Award,
	GraduationCap,
	Briefcase,
} from "lucide-react";
import { Link as RouterLink } from "react-router-dom";

export function InfoSections() {
	const steps = [
		{
			title: "Busque por Proximidade",
			description:
				"Localize instrutores qualificados perto de você com filtros de preço e rating.",
			icon: Search,
			color: "laBlue.500",
		},
		{
			title: "Agende sua Aula",
			description:
				"Escolha o melhor horário e agende aulas de 2h diretamente pela plataforma.",
			icon: Calendar,
			color: "brand.500",
		},
		{
			title: "Aprenda e Evolua",
			description:
				"Receba feedback, acompanhe sua linha do tempo e conquiste sua autonomia.",
			icon: Award,
			color: "laGreen.500",
		},
	];

	return (
		<Stack gap={0} bg="bg.canvas">
			{/* How it Works Section */}
			<Box py={24}>
				<Container maxW="container.xl">
					<Stack gap={16}>
						<Stack
							textAlign="center"
							gap={4}
							maxW="700px"
							mx="auto">
							<Heading fontSize="3xl" fontWeight="800">
								Como Funciona
							</Heading>
							<Text color="text.muted" fontSize="lg">
								Três passos simples para você começar sua
								jornada com total controle.
							</Text>
						</Stack>

						<SimpleGrid columns={{ base: 1, md: 3 }} gap={8}>
							{steps.map((step, index) => (
								<Box
									key={step.title}
									bg="surface.panel"
									p={10}
									borderRadius="3xl"
									border="1px solid"
									borderColor="border.subtle"
									transition="all 0.3s"
									_hover={{
										transform: "translateY(-8px)",
										boxShadow: "lg",
										borderColor: "brand.200",
									}}>
									<Stack align="center" textAlign="center" gap={6}>
										<Box position="relative">
											<Circle
												size={16}
												bg="surface.muted"
												color={step.color}>
												<step.icon size={32} />
											</Circle>
											<Circle
												size={6}
												bg="brand.500"
												color="white"
												fontSize="xs"
												fontWeight="bold"
												position="absolute"
												top={0}
												right={0}
												border="2px solid"
												borderColor="bg.canvas">
												{index + 1}
											</Circle>
										</Box>
										<Stack gap={2}>
											<Text
												fontSize="xl"
												fontWeight="bold">
												{step.title}
											</Text>
											<Text color="text.muted">
												{step.description}
											</Text>
										</Stack>
									</Stack>
								</Box>
							))}
						</SimpleGrid>
					</Stack>
				</Container>
			</Box>

			{/* Roles Sections */}
			<Box py={24} bg="bg.muted">
				<Container maxW="container.xl">
					<SimpleGrid columns={{ base: 1, lg: 2 }} gap={12}>
						{/* For Students */}
						<Box
							p={10}
							rounded="3xl"
							bg="surface.panel"
							border="1px solid"
							borderColor="border.subtle"
							transition="all 0.3s"
							_hover={{ boxShadow: "lg", transform: "translateY(-4px)" }}>
							<Stack gap={8}>
								<Icon
									as={GraduationCap}
									w={10}
									h={10}
									color="brand.500"
								/>
								<Stack gap={4}>
									<Heading fontSize="2xl" fontWeight="800">
										Para Alunos
									</Heading>
									<Text color="text.muted">
										Encontre o instrutor ideal para sua
										necessidade, seja para primeira
										habilitação ou para perder o medo de
										dirigir.
									</Text>
								</Stack>
								<Button
									asChild
									colorPalette="brand"
									size="lg"
									rounded="full"
									w="fit-content">
									<RouterLink to="/register">
										Quero Aprender
									</RouterLink>
								</Button>
							</Stack>
						</Box>

						{/* For Instructors */}
						<Box
							p={10}
							rounded="3xl"
							bg="surface.panel"
							border="1px solid"
							borderColor="border.subtle"
							transition="all 0.3s"
							_hover={{ boxShadow: "lg", transform: "translateY(-4px)" }}>
							<Stack gap={8}>
								<Icon
									as={Briefcase}
									w={10}
									h={10}
									color="laBlue.500"
								/>
								<Stack gap={4}>
									<Heading fontSize="2xl" fontWeight="800">
										Para Instrutores
									</Heading>
									<Text color="text.muted">
										Digitalize sua agenda, aumente sua
										visibilidade e foque no que você faz de
										melhor: ensinar.
									</Text>
								</Stack>
								<Button
									asChild
									variant="outline"
									size="lg"
									rounded="full"
									w="fit-content">
									<RouterLink to="/instructors/register">
										Seja Instrutor
									</RouterLink>
								</Button>
							</Stack>
						</Box>
					</SimpleGrid>
				</Container>
			</Box>

			{/* Stats Section */}
			<Box py={24}>
				<Container maxW="container.xl">
					<Stack gap={16}>
						<Stack
							textAlign="center"
							gap={4}
							maxW="700px"
							mx="auto">
							<Heading fontSize="3xl" fontWeight="800">
								Nossos Números
							</Heading>
							<Text color="text.muted" fontSize="lg">
								A LinkAuto cresce a cada dia, conectando
								confiança em todo o país.
							</Text>
						</Stack>

						<SimpleGrid columns={{ base: 1, sm: 2, md: 4 }} gap={8}>
							{[
								{ label: "Instrutores Ativos", val: "+500" },
								{ label: "Aulas Realizadas", val: "+10k" },
								{ label: "Média de Avaliação", val: "4.9/5" },
								{ label: "Suporte Dedicado", val: "24h" },
							].map((s) => (
								<Box
									key={s.label}
									bg="surface.panel"
									p={8}
									rounded="2xl"
									border="1px solid"
									borderColor="border.subtle"
									textAlign="center"
									transition="all 0.3s"
									_hover={{ boxShadow: "md" }}>
									<Stack gap={2}>
										<Text
											fontSize="4xl"
											fontWeight="800"
											color="brand.500">
											{s.val}
										</Text>
										<Text
											fontWeight="bold"
											fontSize="sm"
											color="text.muted">
											{s.label}
										</Text>
									</Stack>
								</Box>
							))}
						</SimpleGrid>
					</Stack>
				</Container>
			</Box>
		</Stack>
	);
}
