import {
	Box,
	Button,
	Container,
	Heading,
	SimpleGrid,
	Stack,
	Text,
	Circle,
	Icon,
	Flex,
} from "@chakra-ui/react";
import {
	HeartPulse,
	RotateCcw,
	PlusCircle,
	Search,
	Star,
	Quote,
} from "lucide-react";
import { Link as RouterLink } from "react-router-dom";
import { RatingStars } from "../../components/RatingStars";

export default function LicensedDrivers() {
	return (
		<Stack gap={0} bg="bg.canvas">
			{/* Hero Section */}
			<Box
				py={24}
				bgGradient="to-r"
				gradientFrom="laBlue.600"
				gradientTo="laBlue.800"
				color="white">
				<Container maxW="container.lg">
					<Stack gap={8} textAlign="center" align="center">
						<Heading
							fontSize={{ base: "4xl", md: "6xl" }}
							fontWeight="800"
							letterSpacing="tight"
							lineHeight="1.1">
							Volte a Dirigir com Confiança.
						</Heading>
						<Text fontSize="xl" opacity={0.9} maxW="700px">
							Ter a CNH é apenas o primeiro passo. Se você sente
							insegurança, precisa de reciclagem ou quer adicionar
							uma categoria, temos instrutores especializados.
						</Text>
						<Button
							asChild
							size="xl"
							rounded="full"
							bg="white"
							color="laBlue.700"
							_hover={{ bg: "gray.100" }}
							px={10}
							fontWeight="bold">
							<RouterLink to="/search">
								Encontrar Instrutor Especializado{" "}
								<Search size={20} />
							</RouterLink>
						</Button>
					</Stack>
				</Container>
			</Box>

			{/* Use Cases Section */}
			<Box py={24}>
				<Container maxW="container.xl">
					<Stack gap={16}>
						<Stack textAlign="center" gap={4}>
							<Heading fontSize="3xl" fontWeight="800">
								Como podemos te ajudar hoje?
							</Heading>
							<Text color="text.muted" fontSize="lg">
								Soluções personalizadas para quem já possui
								habilitação.
							</Text>
						</Stack>

						<SimpleGrid columns={{ base: 1, md: 3 }} gap={8}>
							<UseCaseCard
								icon={HeartPulse}
								title="Perder o Medo"
								desc="Amaxofobia é real. Nossos instrutores são treinados psicologicamente para te dar calma e controle absoluto do veículo."
							/>
							<UseCaseCard
								icon={RotateCcw}
								title="Reciclagem Prática"
								desc="Ficou muito tempo sem dirigir? Retome os reflexos e as leis de trânsito em vias urbanas e rodovias com segurança."
							/>
							<UseCaseCard
								icon={PlusCircle}
								title="Adição de Categoria"
								desc="Prepare-se para o exame de Moto ou Caminhão com quem entende do assunto e maximize suas chances de aprovação."
							/>
						</SimpleGrid>
					</Stack>
				</Container>
			</Box>

			{/* Why Choose Section */}
			<Box py={24} bg="bg.muted">
				<Container maxW="container.xl">
					<SimpleGrid
						columns={{ base: 1, lg: 2 }}
						gap={16}
						alignItems="center">
						<Box
							p={8}
							bg="surface.panel"
							borderRadius="3xl"
							border="1px solid"
							borderColor="border.subtle">
							<Stack gap={8}>
								<Quote
									size={48}
									color="var(--chakra-colors-brand-500)"
									opacity={0.3}
								/>
								<Text
									fontSize="xl"
									fontStyle="italic"
									lineHeight="tall">
									"Depois de 5 anos com a carteira na gaveta,
									achei que nunca mais dirigiria. O instrutor
									da LinkAuto foi paciente e em 4 aulas eu já
									estava indo pro trabalho de carro sozinha."
								</Text>
								<Flex align="center" gap={4}>
									<Circle
										size={12}
										bg="laBlue.100"
										color="laBlue.600"
										fontWeight="bold">
										J
									</Circle>
									<Box>
										<Text fontWeight="bold">
											Juliana Mendes
										</Text>
										<RatingStars
											rating={5}
											reviewsCount={0}
										/>
									</Box>
								</Flex>
							</Stack>
						</Box>
						<Stack gap={8}>
							<Heading fontSize="3xl" fontWeight="800">
								Por que escolher o LinkAuto?
							</Heading>
							<Stack gap={6}>
								<BenefitItem
									title="Instrutores Pacientes"
									desc="Filtre por especialistas em condutores habilitados com alta taxa de recomendação."
								/>
								<BenefitItem
									title="Foco na Sua Insegurança"
									desc="As aulas são moldadas para o SEU desafio: baliza, ladeira, rodovia ou trânsito pesado."
								/>
								<BenefitItem
									title="Sem Pacotes Engessados"
									desc="Agende apenas uma aula para testar ou quantas precisar para se sentir seguro."
								/>
							</Stack>
						</Stack>
					</SimpleGrid>
				</Container>
			</Box>
		</Stack>
	);
}

function UseCaseCard({
	icon: LucideIcon,
	title,
	desc,
}: {
	icon: React.ElementType;
	title: string;
	desc: string;
}) {
	return (
		<Box
			p={10}
			bg="surface.panel"
			borderRadius="3xl"
			border="1px solid"
			borderColor="border.subtle"
			transition="all 0.3s"
			_hover={{ transform: "translateY(-8px)", boxShadow: "lg" }}>
			<Stack gap={6}>
				<Circle size={14} bg="brand.50" color="brand.500">
					<LucideIcon size={28} />
				</Circle>
				<Stack gap={2}>
					<Text fontSize="xl" fontWeight="bold">
						{title}
					</Text>
					<Text color="text.muted">{desc}</Text>
				</Stack>
			</Stack>
		</Box>
	);
}

function BenefitItem({ title, desc }: { title: string; desc: string }) {
	return (
		<Stack direction="row" gap={4}>
			<Icon as={Star} color="brand.500" mt={1} />
			<Stack gap={1}>
				<Text fontWeight="bold" fontSize="lg">
					{title}
				</Text>
				<Text color="text.muted">{desc}</Text>
			</Stack>
		</Stack>
	);
}
