import {
	Box,
	Container,
	Heading,
	SimpleGrid,
	Stack,
	Text,
} from "@chakra-ui/react";
import { Mail, Users, Car, Clock } from "lucide-react";

const channels = [
	{
		icon: Mail,
		title: "Atendimento geral",
		description: "contato@linkauto.com.br",
	},
	{
		icon: Users,
		title: "Suporte para alunos",
		description: "alunos@linkauto.com.br",
	},
	{
		icon: Car,
		title: "Suporte para instrutores",
		description: "instrutores@linkauto.com.br",
	},
	{
		icon: Clock,
		title: "Horário de atendimento",
		description: "Segunda a sexta, das 9h às 18h",
	},
];

export default function Contact() {
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
							Fale com a LinkAuto
						</Heading>
						<Text fontSize="lg" color="text.muted" maxW="720px">
							Dúvidas sobre agendamento, credenciamento ou sua conta? Escolha
							o canal abaixo e nossa equipe responderá o mais rápido possível.
						</Text>
					</Stack>
				</Container>
			</Box>

			<Box py={16}>
				<Container maxW="container.lg">
					<SimpleGrid columns={{ base: 1, md: 2 }} gap={8}>
						{channels.map((channel) => (
							<Stack
								key={channel.title}
								direction="row"
								gap={4}
								p={6}
								bg="surface.panel"
								border="1px solid"
								borderColor="border.subtle"
								borderRadius="2xl"
								align="center">
								<channel.icon
									size={24}
									color="var(--chakra-colors-brand-500)"
								/>
								<Stack gap={1}>
									<Text fontWeight="bold">{channel.title}</Text>
									<Text color="text.muted" fontSize="sm">
										{channel.description}
									</Text>
								</Stack>
							</Stack>
						))}
					</SimpleGrid>
				</Container>
			</Box>
		</Stack>
	);
}
