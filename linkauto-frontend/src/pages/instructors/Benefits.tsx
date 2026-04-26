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
	TrendingUp,
	CalendarClock,
	Users,
	Wallet,
	ShieldCheck,
	CheckCircle2,
} from "lucide-react";
import { Link as RouterLink } from "react-router-dom";

export default function Benefits() {
	const benefits = [
		{
			title: "Ganhe até 3x mais",
			description: "Elimine a taxa abusiva das autoescolas e fique com até 85% do valor de cada aula dada.",
			icon: TrendingUp,
			color: "laGreen.500",
		},
		{
			title: "Autonomia Total",
			description: "Você define seus horários, locais de atendimento e o valor da sua hora/aula.",
			icon: CalendarClock,
			color: "brand.500",
		},
		{
			title: "Mais Alunos",
			description: "Sua visibilidade aumenta com nosso marketing. Alunos te encontram por geolocalização.",
			icon: Users,
			color: "laBlue.500",
		},
		{
			title: "Pagamentos Seguros",
			description: "Receba seus ganhos semanalmente via PIX de forma automática e transparente.",
			icon: Wallet,
			color: "brand.500",
		},
	];

	return (
		<Stack gap={0} bg="bg.canvas">
			{/* Hero Section */}
			<Box py={24} bgGradient="to-b" gradientFrom="laBlue.600" gradientTo="laBlue.800" color="white">
				<Container maxW="container.lg">
					<Stack gap={8} textAlign="center" align="center">
						<Heading
							fontSize={{ base: "4xl", md: "6xl" }}
							fontWeight="800"
							letterSpacing="tight"
							lineHeight="1.1">
							Seja dono da sua agenda e{" "}
							<Text as="span" color="laGreen.400">
								Ganhe até 3x mais.
							</Text>
						</Heading>
						<Text fontSize="xl" opacity={0.9} maxW="700px">
							A LinkAuto é a plataforma que valoriza o instrutor credenciado. 
							Saia do modelo tradicional e aumente sua lucratividade hoje mesmo.
						</Text>
						<Button asChild size="xl" rounded="full" bg="white" color="laBlue.700" _hover={{ bg: "gray.100" }} px={10} fontWeight="bold">
							<RouterLink to="/register">
								Começar Agora <ArrowRight size={20} />
							</RouterLink>
						</Button>
					</Stack>
				</Container>
			</Box>

			{/* Benefits Grid */}
			<Box py={24}>
				<Container maxW="container.xl">
					<SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} gap={8}>
						{benefits.map((benefit) => (
							<Box 
								key={benefit.title} 
								p={10} 
								bg="surface.panel" 
								borderRadius="3xl" 
								border="1px solid" 
								borderColor="border.subtle" 
								transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)" 
								_hover={{ transform: "translateY(-12px)", boxShadow: "2xl", borderColor: "brand.300" }}
							>
								<Stack gap={6}>
									<Circle size={14} bg="brand.50" color={benefit.color}>
										<benefit.icon size={28} />
									</Circle>
									<Stack gap={2}>
										<Text fontSize="xl" fontWeight="800" color="text.primary">{benefit.title}</Text>
										<Text color="text.muted" lineHeight="tall">{benefit.description}</Text>
									</Stack>
								</Stack>
							</Box>
						))}
					</SimpleGrid>
				</Container>
			</Box>

			{/* Comparison Section */}
			<Box py={24} bg="bg.muted">
				<Container maxW="container.xl">
					<SimpleGrid columns={{ base: 1, lg: 2 }} gap={16} alignItems="center">
						<Stack gap={8}>
							<Heading fontSize="3xl" fontWeight="800">Liberdade Financeira Real</Heading>
							<Text fontSize="lg" color="text.muted">
								Nas autoescolas tradicionais, você recebe uma pequena fração do que o aluno paga. 
								Na LinkAuto, a transparência é a nossa base.
							</Text>
							<Stack gap={4}>
								<ComparisonRow label="Sua parcela por aula" val1="30%" val2="85%" />
								<ComparisonRow label="Gestão de Alunos" val1="Manual" val2="Automática" />
								<ComparisonRow label="Controle de Horários" val1="Rígido" val2="Flexível" />
							</Stack>
						</Stack>
						<Box bg="surface.panel" p={12} borderRadius="3xl" border="1px solid" borderColor="border.subtle" shadow="xl">
							<Stack gap={8} textAlign="center" align="center">
								<Circle size={16} bg="laGreen.50" color="laGreen.500">
									<CheckCircle2 size={32} />
								</Circle>
								<Stack gap={2}>
									<Heading fontSize="2xl" fontWeight="800">Faça o seu preço</Heading>
									<Text color="text.muted">
										No LinkAuto você decide quanto vale a sua hora. Instrutores top-rated 
										estão faturando mais de R$ 6.000 mensais.
									</Text>
								</Stack>
								<Separator />
								<Button asChild size="lg" colorPalette="brand" rounded="full" w="full">
									<RouterLink to="/instructors/simulator">Simular Meus Ganhos</RouterLink>
								</Button>
							</Stack>
						</Box>
					</SimpleGrid>
				</Container>
			</Box>

			{/* Security Section */}
			<Box py={24}>
				<Container maxW="container.xl">
					<Stack gap={12} align="center" textAlign="center">
						<Stack gap={4} maxW="700px">
							<Heading fontSize="3xl" fontWeight="800">Sua Segurança é Nossa Prioridade</Heading>
							<Text color="text.muted" fontSize="lg">
								Não apenas validamos alunos, mas também garantimos que você tenha suporte 24h em qualquer situação.
							</Text>
						</Stack>
						<SimpleGrid columns={{ base: 1, md: 3 }} gap={8} w="full">
							<SecurityFeature icon={ShieldCheck} title="Alunos Verificados" desc="Todos os alunos passam por verificação de identidade antes do primeiro agendamento." />
							<SecurityFeature icon={CalendarClock} title="Check-in GPS" desc="Monitoramos o início e fim de cada aula via GPS para sua proteção." />
							<SecurityFeature icon={Wallet} title="Garantia de Pagamento" desc="Receba mesmo em caso de cancelamentos de última hora (conforme sua política)." />
						</SimpleGrid>
					</Stack>
				</Container>
			</Box>
		</Stack>
	);
}

function ComparisonRow({ label, val1, val2 }: { label: string; val1: string; val2: string }) {
	return (
		<Box display="flex" justifyContent="space-between" alignItems="center" p={4} borderRadius="xl" bg="bg.canvas" border="1px solid" borderColor="border.subtle">
			<Text fontWeight="bold" fontSize="sm">{label}</Text>
			<Stack direction="row" gap={8}>
				<Text color="text.muted" fontSize="sm">Autoescola: {val1}</Text>
				<Text color="laGreen.500" fontWeight="800" fontSize="sm">LinkAuto: {val2}</Text>
			</Stack>
		</Box>
	);
}

function SecurityFeature({ icon: LucideIcon, title, desc }: { icon: any; title: string; desc: string }) {
	return (
		<Stack align="center" gap={4} p={8}>
			<Circle size={12} bg="surface.muted" color="brand.500">
				<LucideIcon size={24} />
			</Circle>
			<Text fontWeight="bold" fontSize="lg">{title}</Text>
			<Text color="text.muted" fontSize="sm">{desc}</Text>
		</Stack>
	);
}
