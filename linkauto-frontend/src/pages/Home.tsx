import { ArrowRight, Compass, ShieldCheck, TimerReset } from "lucide-react";
import {
	Box,
	Button,
	Container,
	Grid,
	Heading,
	HStack,
	Image,
	SimpleGrid,
	Stack,
	Text,
} from "@chakra-ui/react";

import { BrandLockup } from "../components/BrandLockup";

interface HomeProps {
	readonly isAuthenticated: boolean;
	readonly onOpenLogin: () => void;
	readonly onOpenSearch: () => void;
}

const references = [
	{
		title: "Landing institucional",
		source: "/design/landpage_example.png",
	},
	{
		title: "Busca com mapa",
		source: "/design/instructor_search_mapview_example.png",
	},
	{
		title: "Painel do instrutor",
		source: "/design/instructor_dashboard_example.png",
	},
	{
		title: "Painel administrativo",
		source: "/design/admin_dashboard_example.png",
	},
];

const highlights = [
	{
		title: "Busca geolocalizada",
		description:
			"Encontre instrutores credenciados por bairro, distancia e especialidade.",
		icon: Compass,
	},
	{
		title: "Governanca de perfis",
		description:
			"Fluxo de aprovacao administrativa para manter a qualidade e a seguranca da plataforma.",
		icon: ShieldCheck,
	},
	{
		title: "Regras de agenda",
		description:
			"Agendamento com no minimo 2 horas consecutivas e timeline de status para cada reserva.",
		icon: TimerReset,
	},
];

export default function Home({
	isAuthenticated,
	onOpenLogin,
	onOpenSearch,
}: HomeProps) {
	return (
		<Stack minH="100vh" pb={14}>
			<Box
				bg="surface.panel"
				borderBottom="1px solid"
				borderColor="border.default"
				position="sticky"
				top={0}
				zIndex={30}>
				<Container maxW="7xl" py={3.5}>
					<HStack justify="space-between" gap={4}>
						<BrandLockup compact />
						<HStack gap={2}>
							<Button
								variant="ghost"
								color="text.secondary"
								onClick={onOpenSearch}>
								Busca
							</Button>
							{isAuthenticated ? null : (
								<Button
									bg="brand.solid"
									color="text.inverse"
									onClick={onOpenLogin}
									_hover={{ bg: "brand.emphasized" }}>
									Entrar
								</Button>
							)}
						</HStack>
					</HStack>
				</Container>
			</Box>

			<Container maxW="7xl" pt={{ base: 9, md: 14 }}>
				<Grid
					templateColumns={{ base: "1fr", lg: "1.15fr 0.85fr" }}
					gap={8}>
					<Stack gap={6}>
						<Box
							alignSelf="start"
							px={3}
							py={1}
							borderRadius="full"
							bg="brand.muted"
							color="brand.emphasized"
							fontSize="xs"
							fontWeight="700"
							letterSpacing="0.08em"
							textTransform="uppercase">
							LinkAuto • MVP v1
						</Box>

						<Stack gap={3.5}>
							<Heading
								fontSize={{ base: "3xl", md: "4xl" }}
								lineHeight="1.1"
								color="text.primary">
								Conecte alunos e instrutores de transito com uma
								busca clara, local e confiavel.
							</Heading>
							<Text
								fontSize={{ base: "md", md: "lg" }}
								lineHeight="1.6"
								color="text.secondary"
								maxW="680px">
								A plataforma aplica validacao de instrutores,
								agendamento com regras de slots e fluxo de
								status para dar previsibilidade ao aluno e ao
								instrutor.
							</Text>
						</Stack>

						<HStack gap={3} flexWrap="wrap">
							<Button
								h="48px"
								px={6}
								bg="brand.solid"
								color="text.inverse"
								fontWeight="700"
								onClick={
									isAuthenticated ? onOpenSearch : onOpenLogin
								}
								_hover={{ bg: "brand.emphasized" }}>
								{isAuthenticated
									? "Ir para busca"
									: "Acessar plataforma"}
								<ArrowRight size={16} />
							</Button>
							<Button
								h="48px"
								px={6}
								variant="outline"
								borderColor="border.default"
								color="text.secondary"
								onClick={onOpenSearch}>
								Ver busca demo
							</Button>
						</HStack>

						<SimpleGrid columns={{ base: 1, md: 3 }} gap={3.5}>
							{highlights.map((item) => {
								const Icon = item.icon;
								return (
									<Box
										key={item.title}
										bg="surface.panel"
										border="1px solid"
										borderColor="border.default"
										borderRadius="2xl"
										p={4}>
										<HStack gap={2.5} align="start">
											<Box
												w="34px"
												h="34px"
												borderRadius="lg"
												display="grid"
												placeItems="center"
												bg="accent.muted"
												color="accent.emphasized">
												<Icon
													size={18}
													aria-hidden="true"
												/>
											</Box>
											<Stack gap={1}>
												<Text
													fontWeight="700"
													color="text.primary">
													{item.title}
												</Text>
												<Text
													fontSize="sm"
													color="text.muted"
													lineHeight="1.5">
													{item.description}
												</Text>
											</Stack>
										</HStack>
									</Box>
								);
							})}
						</SimpleGrid>
					</Stack>

					<Box
						border="1px solid"
						borderColor="border.default"
						borderRadius="3xl"
						bg="surface.panel"
						p={4}
						boxShadow="0 28px 48px rgba(17, 24, 39, 0.08)">
						<Image
							src="/brand/LinkAuto-banner.webp"
							alt="Identidade visual LinkAuto"
							borderRadius="2xl"
							w="100%"
							objectFit="cover"
						/>
						<Text
							mt={3}
							fontSize="sm"
							color="text.muted"
							fontWeight="600">
							Design inspirado em civic tech refinado com foco em
							legibilidade, confianca e velocidade de acao.
						</Text>
					</Box>
				</Grid>
			</Container>

			<Container maxW="7xl" pt={12}>
				<Stack gap={4}>
					<Heading
						fontSize={{ base: "xl", md: "2xl" }}
						color="text.primary">
						Referencias visuais usadas nesta entrega
					</Heading>
					<Text color="text.muted" maxW="720px">
						As composicoes abaixo foram usadas como guia para
						landing, mapa de busca e dashboards, com adaptacao para
						os fluxos da especificacao de usuarios e agendamentos.
					</Text>
				</Stack>

				<SimpleGrid mt={5} columns={{ base: 1, md: 2 }} gap={4}>
					{references.map((reference) => (
						<Box
							key={reference.title}
							bg="surface.panel"
							border="1px solid"
							borderColor="border.default"
							borderRadius="2xl"
							overflow="hidden">
							<Image
								src={reference.source}
								alt={reference.title}
								w="100%"
								h="220px"
								objectFit="cover"
							/>
							<Text
								px={4}
								py={3}
								fontWeight="700"
								color="text.primary">
								{reference.title}
							</Text>
						</Box>
					))}
				</SimpleGrid>
			</Container>
		</Stack>
	);
}
