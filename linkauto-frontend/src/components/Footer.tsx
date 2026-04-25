import {
	Box,
	Container,
	SimpleGrid,
	Stack,
	Text,
	Link,
	Separator,
	HStack,
	Circle,
} from "@chakra-ui/react";
import { Link as RouterLink } from "react-router-dom";
import { BrandLockup } from "./BrandLockup";
import { Share2, Globe, Mail } from "lucide-react";

const ListHeader = ({ children }: { children: React.ReactNode }) => {
	return (
		<Text
			fontWeight="800"
			fontSize="md"
			mb={4}
			color="text.primary"
			textTransform="uppercase"
			letterSpacing="widest">
			{children}
		</Text>
	);
};

const SocialButton = ({
	children,
	label,
	href,
}: {
	children: React.ReactNode;
	label: string;
	href: string;
}) => {
	return (
		<Link href={href} aria-label={label} className="group">
			<Circle
				size={10}
				bg="bg.muted"
				transition="all 0.3s"
				_groupHover={{
					bg: "brand.500",
					color: "white",
					transform: "translateY(-4px)",
				}}>
				{children}
			</Circle>
		</Link>
	);
};

export function Footer() {
	return (
		<Box
			as="footer"
			role="contentinfo"
			bg="surface.panel"
			color="text.muted"
			borderTop="1px solid"
			borderColor="border.subtle"
			pt={12}
			pb={12}
			height="sm">
			<Container maxW="container.xl">
				<SimpleGrid
					templateColumns={{ base: "1fr", lg: "2fr 1fr 1fr 1fr" }}
					gap={12}>
					<Stack gap={8}>
						<BrandLockup />
						<Text fontSize="md" lineHeight="tall" maxW="320px">
							A liberdade de dirigir começa com a conexão certa.
							Encontre instrutores validados e agende suas aulas
							com total segurança e transparência.
						</Text>
						<HStack gap={4}>
							<SocialButton label="Website Oficial" href="#">
								<Globe size={18} />
							</SocialButton>
							<SocialButton label="E-mail de Contato" href="#">
								<Mail size={18} />
							</SocialButton>
							<SocialButton label="Compartilhar" href="#">
								<Share2 size={18} />
							</SocialButton>
						</HStack>
					</Stack>

					<Stack align="flex-start" gap={3}>
						<ListHeader>Alunos</ListHeader>
						<Link
							asChild
							variant="plain"
							color="inherit"
							_hover={{ color: "brand.500", fontWeight: "600" }}>
							<RouterLink to="/students/first-license">
								Primeira Habilitação
							</RouterLink>
						</Link>
						<Link
							asChild
							variant="plain"
							color="inherit"
							_hover={{ color: "brand.500", fontWeight: "600" }}>
							<RouterLink to="/search">
								Buscar Instrutor
							</RouterLink>
						</Link>
						<Link
							asChild
							variant="plain"
							color="inherit"
							_hover={{ color: "brand.500", fontWeight: "600" }}>
							<RouterLink to="/student/lessons">
								Minhas Aulas
							</RouterLink>
						</Link>
					</Stack>

					<Stack align="flex-start" gap={3}>
						<ListHeader>Instrutores</ListHeader>
						<Link
							asChild
							variant="plain"
							color="inherit"
							_hover={{ color: "brand.500", fontWeight: "600" }}>
							<RouterLink to="/instructors/register">
								Cadastrar como Instrutor
							</RouterLink>
						</Link>
						<Link
							asChild
							variant="plain"
							color="inherit"
							_hover={{ color: "brand.500", fontWeight: "600" }}>
							<RouterLink to="/instructor/students">
								Painel do Instrutor
							</RouterLink>
						</Link>
						<Link
							asChild
							variant="plain"
							color="inherit"
							_hover={{ color: "brand.500", fontWeight: "600" }}>
							<RouterLink to="/instructor/vehicles">
								Meus Veículos
							</RouterLink>
						</Link>
					</Stack>

					<Stack align="flex-start" gap={3}>
						<ListHeader>Institucional</ListHeader>
						<Link
							asChild
							variant="plain"
							color="inherit"
							_hover={{ color: "brand.500", fontWeight: "600" }}>
							<RouterLink to="/about">Sobre Nós</RouterLink>
						</Link>
						<Link
							asChild
							variant="plain"
							color="inherit"
							_hover={{ color: "brand.500", fontWeight: "600" }}>
							<RouterLink to="/contact">Contato</RouterLink>
						</Link>
						<Link
							asChild
							variant="plain"
							color="inherit"
							_hover={{ color: "brand.500", fontWeight: "600" }}>
							<RouterLink to="/terms">Termos de Uso</RouterLink>
						</Link>
					</Stack>
				</SimpleGrid>

				<Separator mt={16} mb={8} borderColor="border.subtle" />

				<Stack
					direction={{ base: "column", md: "row" }}
					justify="space-between"
					align="center"
					gap={4}>
					<Text fontSize="sm" fontWeight="500">
						© 2026 LinkAuto. Todos os direitos reservados.
					</Text>
					<HStack gap={6}>
						<Link
							asChild
							variant="plain"
							fontSize="xs"
							_hover={{ color: "brand.500" }}>
							<RouterLink to="/privacy">Privacidade</RouterLink>
						</Link>
						<Link
							asChild
							variant="plain"
							fontSize="xs"
							_hover={{ color: "brand.500" }}>
							<RouterLink to="/cookies">Cookies</RouterLink>
						</Link>
					</HStack>
				</Stack>
			</Container>
		</Box>
	);
}
