import {
	Box,
	Flex,
	HStack,
	Button,
	IconButton,
	MenuRoot,
	MenuTrigger,
	MenuContent,
	MenuItem,
	useWindowScroll,
} from "@chakra-ui/react";
import { Link as RouterLink } from "react-router-dom";
import { Menu, X, ChevronDown, User, Shield } from "lucide-react";
import { BrandLockup } from "./BrandLockup";
import { useState, useEffect } from "react";

export function Navbar() {
	const [scrolled, setScrolled] = useState(false);

	useEffect(() => {
		const handleScroll = () => {
			setScrolled(window.scrollY > 10);
		};
		window.addEventListener("scroll", handleScroll);
		return () => window.removeEventListener("scroll", handleScroll);
	}, []);

	return (
		<Box
			as="nav"
			position="fixed"
			top={0}
			w="full"
			zIndex={100}
			h={16}
			bg={scrolled ? "surface.panel" : "transparent"}
			backdropFilter={scrolled ? "blur(12px)" : "none"}
			borderBottom={scrolled ? "1px solid" : "none"}
			borderColor="border.subtle"
			transition="all 0.3s ease-in-out"
			boxShadow={
				scrolled ? "0 4px 20px -2px rgba(0, 0, 0, 0.05)" : "none"
			}>
			<Flex
				h={16}
				alignItems="center"
				justifyContent="space-between"
				maxW="container.xl"
				mx="auto"
				px={{ base: 4, md: 8 }}>
				<BrandLockup compact />

				{/* Desktop Menu */}
				<HStack gap={8} display={{ base: "none", lg: "flex" }}>
					<Button
						asChild
						variant="ghost"
						fontWeight="medium"
						color="text.primary"
						_hover={{ bg: "surface.muted" }}>
						<RouterLink to="/">Explorar</RouterLink>
					</Button>

					<MenuRoot>
						<MenuTrigger asChild>
							<Button
								variant="ghost"
								fontWeight="medium"
								color="text.primary"
								_hover={{ bg: "surface.muted" }}>
								Para Alunos <ChevronDown size={16} />
							</Button>
						</MenuTrigger>
						<MenuContent
							minW="220px"
							rounded="xl"
							shadow="md"
							p={2}>
							<MenuItem
								value="first-license"
								cursor="pointer"
								rounded="md"
								asChild>
								<RouterLink to="/students/first-license">
									Primeira Habilitação
								</RouterLink>
							</MenuItem>
							<MenuItem
								value="licensed"
								cursor="pointer"
								rounded="md"
								asChild>
								<RouterLink to="/students/licensed">
									Habilitados
								</RouterLink>
							</MenuItem>
							<MenuItem
								value="how-it-works"
								cursor="pointer"
								rounded="md"
								asChild>
								<RouterLink to="/students/how-it-works">
									Como Funciona
								</RouterLink>
							</MenuItem>
							<MenuItem
								value="search"
								color="laBlue.600"
								fontWeight="bold"
								cursor="pointer"
								rounded="md"
								asChild>
								<RouterLink to="/login">
									Ver Instrutores
								</RouterLink>
							</MenuItem>
						</MenuContent>
					</MenuRoot>

					<MenuRoot>
						<MenuTrigger asChild>
							<Button
								variant="ghost"
								fontWeight="medium"
								color="text.primary"
								_hover={{ bg: "surface.muted" }}>
								Para Instrutores <ChevronDown size={16} />
							</Button>
						</MenuTrigger>
						<MenuContent
							minW="220px"
							rounded="xl"
							shadow="md"
							p={2}>
							<MenuItem
								value="register"
								color="laGreen.600"
								fontWeight="bold"
								cursor="pointer"
								rounded="md"
								asChild>
								<RouterLink to="/register?role=instructor">
									Cadastre-se
								</RouterLink>
							</MenuItem>
							<MenuItem
								value="how-it-works"
								cursor="pointer"
								rounded="md"
								asChild>
								<RouterLink to="/instructors/how-it-works">
									Como Funciona
								</RouterLink>
							</MenuItem>
							<MenuItem
								value="benefits"
								cursor="pointer"
								rounded="md"
								asChild>
								<RouterLink to="/instructors/benefits">
									Vantagens
								</RouterLink>
							</MenuItem>
							<MenuItem
								value="simulator"
								cursor="pointer"
								rounded="md"
								asChild>
								<RouterLink to="/instructors/simulator">
									Simulador
								</RouterLink>
							</MenuItem>
						</MenuContent>
					</MenuRoot>

					<Button
						asChild
						variant="ghost"
						fontWeight="medium"
						color="text.primary"
						_hover={{ bg: "surface.muted" }}>
						<RouterLink to="/about">Sobre</RouterLink>
					</Button>
					<Button
						asChild
						variant="ghost"
						fontWeight="medium"
						color="text.primary"
						_hover={{ bg: "surface.muted" }}>
						<RouterLink to="/contact">Contato</RouterLink>
					</Button>
				</HStack>

				{/* Desktop CTAs */}
				<HStack gap={4} display={{ base: "none", lg: "flex" }}>
					<Button
						asChild
						variant="ghost"
						fontWeight="bold"
						color="text.secondary">
						<RouterLink to="/login">Entrar</RouterLink>
					</Button>
					<Button
						asChild
						variant="solid"
						colorScheme="laBlue"
						rounded="full"
						px={6}
						shadow="md">
						<RouterLink to="/register">Comece agora</RouterLink>
					</Button>
				</HStack>

				{/* Mobile Menu Toggle */}
				<IconButton
					display={{ base: "flex", lg: "none" }}
					variant="ghost"
					aria-label="Open menu"
					color="text.primary">
					<Menu />
				</IconButton>
			</Flex>
		</Box>
	);
}
