import { useState } from "react";
import {
	Box,
	Container,
	Heading,
	SimpleGrid,
	Stack,
	Text,
	Input,
	Field,
	Separator,
	Button,
	Circle,
} from "@chakra-ui/react";
import { Landmark, PiggyBank, ArrowRight } from "lucide-react";
import { Link as RouterLink } from "react-router-dom";

export default function Simulator() {
	const [lessonPrice, setLessonPrice] = useState(80);
	const [lessonsPerWeek, setLessonsPerWeek] = useState(25);

	const monthlyRevenue = lessonPrice * lessonsPerWeek * 4;
	const platformFee = monthlyRevenue * 0.15;
	const netEarnings = monthlyRevenue - platformFee;
	
	// Estimated school earnings (assuming instructor keep 35% of a R$ 120 lesson)
	const schoolEstimated = 120 * lessonsPerWeek * 4 * 0.35;

	return (
		<Stack gap={0} bg="bg.canvas">
			{/* Hero Section */}
			<Box py={24} bgGradient="to-b" gradientFrom="laGreen.600" gradientTo="laGreen.800" color="white">
				<Container maxW="container.lg">
					<Stack gap={6} textAlign="center" align="center">
						<Heading
							fontSize={{ base: "4xl", md: "5xl" }}
							fontWeight="800"
							letterSpacing="tight">
							Potencial de Ganhos.
						</Heading>
						<Text fontSize="lg" opacity={0.9} maxW="600px">
							Use nosso simulador para ver quanto você pode faturar sendo 
							um instrutor autônomo na plataforma LinkAuto.
						</Text>
					</Stack>
				</Container>
			</Box>

			{/* Simulator Section */}
			<Box py={24}>
				<Container maxW="container.xl">
					<SimpleGrid columns={{ base: 1, lg: 2 }} gap={16} alignItems="start">
						{/* Inputs */}
						<Box p={10} bg="surface.panel" borderRadius="3xl" border="1px solid" borderColor="border.subtle" shadow="sm">
							<Stack gap={10}>
								<Stack gap={2}>
									<Heading fontSize="2xl" fontWeight="bold">Personalize sua Simulação</Heading>
									<Text color="text.muted">Ajuste os valores abaixo para refletir sua realidade.</Text>
								</Stack>
								
								<Stack gap={6}>
									<Field.Root>
										<Field.Label fontWeight="bold" mb={2}>Valor da Hora/Aula (R$)</Field.Label>
										<Input 
											type="number" 
											value={lessonPrice} 
											onChange={(e) => setLessonPrice(Number(e.target.value))}
											size="lg"
											borderRadius="xl"
											borderColor="border.emphasized"
											aria-label="Valor da Hora"
										/>
										<Field.HelperText>Média recomendada: R$ 80 - R$ 120</Field.HelperText>
									</Field.Root>

									<Field.Root>
										<Field.Label fontWeight="bold" mb={2}>Aulas por Semana</Field.Label>
										<Input 
											type="number" 
											value={lessonsPerWeek} 
											onChange={(e) => setLessonsPerWeek(Number(e.target.value))}
											size="lg"
											borderRadius="xl"
											borderColor="border.emphasized"
											aria-label="Aulas por Semana"
										/>
										<Field.HelperText>Sugestão: 20 a 35 aulas</Field.HelperText>
									</Field.Root>
								</Stack>
							</Stack>
						</Box>

						{/* Results */}
						<Stack gap={8}>
							<Box 
								p={10} 
								bg="bg.canvas" 
								borderRadius="3xl" 
								border="2px solid" 
								borderColor="laGreen.500" 
								shadow="2xl"
								transition="all 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275)"
								_hover={{ transform: "scale(1.02)" }}
							>
								<Stack gap={6}>
									<Stack direction="row" justify="space-between" align="center">
										<Text fontWeight="bold" color="text.muted">Faturamento Mensal Estimado</Text>
										<Circle size={10} bg="laGreen.50" color="laGreen.500">
											<PiggyBank size={20} />
										</Circle>
									</Stack>
									<Heading fontSize="5xl" fontWeight="900" color="laGreen.600">
										R$ {netEarnings.toLocaleString("pt-BR")}
									</Heading>
									<Separator />
									<Stack gap={3}>
										<ResultRow label="Total Bruto" value={`R$ ${monthlyRevenue.toLocaleString("pt-BR")}`} />
										<ResultRow label="Taxa LinkAuto (15%)" value={`- R$ ${platformFee.toLocaleString("pt-BR")}`} isNegative />
									</Stack>
								</Stack>
							</Box>

							{/* Comparison Mini Card */}
							<Box p={6} bg="surface.panel" borderRadius="2xl" border="1px solid" borderColor="border.subtle">
								<Stack direction="row" gap={4} align="center">
									<Circle size={10} bg="gray.100" color="gray.600">
										<Landmark size={20} />
									</Circle>
									<Box>
										<Text fontSize="sm" color="text.muted">Em uma Autoescola tradicional você ganharia aprox:</Text>
										<Text fontWeight="bold" color="text.primary">R$ {schoolEstimated.toLocaleString("pt-BR")}</Text>
									</Box>
								</Stack>
							</Box>

							<Button asChild size="xl" colorPalette="brand" rounded="full" fontWeight="bold" w="full">
								<RouterLink to="/register">
									Gostei, quero me cadastrar <ArrowRight size={20} />
								</RouterLink>
							</Button>
						</Stack>
					</SimpleGrid>
				</Container>
			</Box>
		</Stack>
	);
}

function ResultRow({ label, value, isNegative = false }: { label: string; value: string; isNegative?: boolean }) {
	return (
		<Box display="flex" justifyContent="space-between">
			<Text fontSize="sm" color="text.muted">{label}</Text>
			<Text fontSize="sm" fontWeight="bold" color={isNegative ? "laStatus.cancelled" : "text.primary"}>{value}</Text>
		</Box>
	);
}
