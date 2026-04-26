import {
	Box,
	Button,
	Container,
	Heading,
	SimpleGrid,
	Stack,
	Text,
	Circle,
	Separator,
} from "@chakra-ui/react";
import {
	ArrowRight,
	ShieldCheck,
	Clock,
	Banknote,
	CheckCircle2,
} from "lucide-react";
import { Link as RouterLink } from "react-router-dom";

export default function FirstLicense() {
	return (
		<Stack gap={0} bg="bg.canvas">
			{/* Hero Section */}
			<Box
				py={24}
				bgGradient="to-b"
				gradientFrom="surface.panel"
				gradientTo="bg.canvas">
				<Container maxW="container.lg">
					<Stack gap={8} textAlign="center" align="center">
						<Heading
							fontSize={{ base: "4xl", md: "6xl" }}
							fontWeight="800"
							letterSpacing="tight"
							lineHeight="1.1">
							Sua CNH com{" "}
							<Text as="span" color="brand.500">
								Liberdade
							</Text>{" "}
							e Transparência.
						</Heading>
						<Text fontSize="xl" color="text.muted" maxW="600px">
							O modelo tradicional de autoescolas é burocrático e
							caro. Com a LinkAuto, você escolhe seu instrutor,
							controla sua agenda e economiza.
						</Text>
						<Button
							asChild
							size="xl"
							rounded="full"
							colorPalette="brand"
							px={10}
							fontWeight="bold">
							<RouterLink to="/register">
								Começar Agora <ArrowRight size={20} />
							</RouterLink>
						</Button>
					</Stack>
				</Container>
			</Box>

			{/* Comparison Section */}
			<Box py={24} bg="bg.muted">
				<Container maxW="container.xl">
					<Stack gap={16}>
						<Heading
							textAlign="center"
							fontSize="3xl"
							fontWeight="800">
							Por que escolher o LinkAuto?
						</Heading>

						<SimpleGrid columns={{ base: 1, md: 2 }} gap={12}>
							<Box
								p={10}
								bg="surface.panel"
								borderRadius="3xl"
								border="1px solid"
								borderColor="border.error"
								transition="all 0.3s"
								_hover={{
									transform: "translateY(-8px)",
									boxShadow:
										"0 20px 40px -12px rgba(0,0,0,0.08)",
									borderColor: "laRed.500",
								}}>
								<Stack gap={6}>
									<Heading
										fontSize="xl"
										color="text.secondary">
										Autoescola Tradicional
									</Heading>
									<Stack gap={4}>
										<HStackItem
											text="Preço fechado e elevado (Média R$ 2.500+)"
											isNegative
										/>
										<HStackItem
											text="Instrutor atribuído aleatoriamente"
											isNegative
										/>
										<HStackItem
											text="Horários rígidos e filas de espera"
											isNegative
										/>
										<HStackItem
											text="Burocracia excessiva no agendamento"
											isNegative
										/>
									</Stack>
								</Stack>
							</Box>

							<Box
								p={10}
								bg="surface.panel"
								borderRadius="3xl"
								border="2px solid"
								borderColor="laGreen.500"
								shadow="xl"
								transition="all 0.3s"
								_hover={{
									transform: "translateY(-8px)",
									boxShadow:
										"0 20px 40px -12px rgba(0,0,0,0.08)",
									borderColor: "laGreen.500",
								}}>
								<Stack gap={6}>
									<Heading fontSize="xl" color="brand.500">
										LinkAuto
									</Heading>
									<Stack gap={4}>
										<HStackItem text="Economia de até 40% nas aulas práticas" />
										<HStackItem text="Você escolhe o instrutor pelo rating e perfil" />
										<HStackItem text="Agende aulas pelo app em segundos" />
										<HStackItem text="Pague apenas pelo que usar (Pay-as-you-go)" />
									</Stack>
								</Stack>
							</Box>
						</SimpleGrid>
					</Stack>
				</Container>
			</Box>

			{/* Security Section */}
			<Box py={24}>
				<Container maxW="container.xl">
					<SimpleGrid
						columns={{ base: 1, lg: 2 }}
						gap={16}
						alignItems="center">
						<Stack gap={8}>
							<Heading fontSize="3xl" fontWeight="800">
								Segurança em Primeiro Lugar
							</Heading>
							<Text fontSize="lg" color="text.muted">
								Sabemos que aprender a dirigir exige confiança.
								Por isso, criamos o sistema de validação mais
								rigoroso do mercado.
							</Text>
							<Stack gap={6}>
								<SecurityItem
									icon={ShieldCheck}
									title="Instrutores Validados"
									desc="Verificamos antecedentes criminais e credenciais do DETRAN de todos os parceiros."
								/>
								<SecurityItem
									icon={Clock}
									title="Acompanhamento em Tempo Real"
									desc="Todas as aulas são registradas via GPS para sua segurança e controle de progresso."
								/>
								<SecurityItem
									icon={Banknote}
									title="Pagamento Seguro"
									desc="O valor da aula só é liberado para o instrutor após a sua confirmação de conclusão."
								/>
							</Stack>
						</Stack>
						<Box
							bg="surface.panel"
							p={12}
							borderRadius="3xl"
							border="1px solid"
							borderColor="border.success"
							transition="all 0.3s"
							_hover={{
								transform: "translateY(-8px)",
								boxShadow: "0 20px 40px -12px rgba(0,0,0,0.08)",
								borderColor: "brand.200",
							}}>
							<Stack gap={6} textAlign="center" align="center">
								<Circle
									size={16}
									bg="brand.50"
									color="brand.500">
									<CheckCircle2 size={32} />
								</Circle>
								<Heading fontSize="2xl">
									Pronto para a CNH?
								</Heading>
								<Text color="text.muted">
									O custo estimado para obter sua CNH através
									da nossa plataforma, incluindo taxas
									estaduais e aulas, é cerca de 30% menor que
									o modelo convencional.
								</Text>
								<Separator />
								<Text fontWeight="bold" fontSize="lg">
									Economia estimada: R$ 800,00
								</Text>
							</Stack>
						</Box>
					</SimpleGrid>
				</Container>
			</Box>
		</Stack>
	);
}

function HStackItem({
	text,
	isNegative = false,
}: {
	text: string;
	isNegative?: boolean;
}) {
	return (
		<Stack direction="row" gap={3} align="center">
			<Circle size={2} bg={isNegative ? "gray.400" : "laGreen.500"} />
			<Text
				fontSize="md"
				color={isNegative ? "text.muted" : "text.primary"}>
				{text}
			</Text>
		</Stack>
	);
}

function SecurityItem({
	icon: LucideIcon,
	title,
	desc,
}: {
	icon: React.ElementType;
	title: string;
	desc: string;
}) {
	return (
		<Stack direction="row" gap={4}>
			<Circle
				size={12}
				bg="surface.muted"
				color="brand.500"
				flexShrink={0}>
				<LucideIcon size={24} />
			</Circle>
			<Stack gap={1}>
				<Text fontWeight="bold" fontSize="lg">
					{title}
				</Text>
				<Text color="text.muted">{desc}</Text>
			</Stack>
		</Stack>
	);
}
