import {
	Box,
	chakra,
	Flex,
	HStack,
	Button,
	IconButton,
	MenuRoot,
	MenuTrigger,
	MenuContent,
	MenuItem,
	MenuPositioner,
	Text,
	DrawerRoot,
	DrawerTrigger,
	DrawerContent,
	DrawerHeader,
	DrawerBody,
	DrawerCloseTrigger,
	Stack,
} from "@chakra-ui/react";
import { Link as RouterLink } from "react-router-dom";
import { Menu, ChevronDown, LogOut } from "lucide-react";
import { BrandLockup } from "./BrandLockup";
import { useState, useEffect } from "react";
import { useSessionStore } from "../state/sessionStore";
import { ProfileSidebar } from "./ProfileSidebar";

export function Navbar() {
	const [scrolled, setScrolled] = useState(false);
	const [isProfileOpen, setIsProfileOpen] = useState(false);
	const [isMobileDrawerOpen, setIsMobileDrawerOpen] = useState(false);
	const { isAuthenticated, session, signOut } = useSessionStore();

	useEffect(() => {
		const handleScroll = () => {
			setScrolled(window.scrollY > 10);
		};
		window.addEventListener("scroll", handleScroll);
		return () => window.removeEventListener("scroll", handleScroll);
	}, []);

	const handleAvatarClick = () => {
		setIsProfileOpen(true);
	};

	const user = session?.user;
	const isStudent = user?.roles?.includes("ALUNO") || user?.roles?.includes("student");
	const isInstructor = user?.roles?.includes("INSTRUTOR") || user?.roles?.includes("instructor");
	const isAdmin = user?.roles?.includes("ADMIN") || user?.roles?.includes("admin");
	const avatarUrl = user?.instructor_profile?.avatar_url ?? user?.student_profile?.avatar_url;

	const displayName =
		user?.student_profile?.full_name?.split(" ")[0] ||
		user?.instructor_profile?.full_name?.split(" ")[0] ||
		user?.email.split("@")[0] ||
		"Usuário";

	return (
		<Box
			as="nav"
			position="fixed"
			top={0}
			w="full"
			zIndex={500}
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
						<MenuPositioner>
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
									color="brand.600"
									fontWeight="bold"
									cursor="pointer"
									rounded="md"
									asChild>
									<RouterLink to="/search">
										Ver Instrutores
									</RouterLink>
								</MenuItem>
							</MenuContent>
						</MenuPositioner>
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
						<MenuPositioner>
							<MenuContent
								minW="220px"
								rounded="xl"
								shadow="md"
								p={2}>
								<MenuItem
									value="register"
									color="brand.600"
									fontWeight="bold"
									cursor="pointer"
									rounded="md"
									asChild>
									<RouterLink to="/register">
										Cadastre-se Agora
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
										Simulador de Ganhos
									</RouterLink>
								</MenuItem>
							</MenuContent>
						</MenuPositioner>
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

				{/* Desktop Actions */}
				<HStack gap={4} display={{ base: "none", lg: "flex" }}>
					{isAuthenticated ? (
						<HStack gap={4}>
							<Button
								variant="ghost"
								h="auto"
								py={1}
								px={2}
								gap={3}
								borderRadius="full"
								onClick={handleAvatarClick}
								aria-haspopup="dialog"
								aria-expanded={isProfileOpen}
								aria-label={`Abrir menu de perfil (${displayName})`}>
								<Box display={{ base: "none", xl: "block" }}>
									<Text
										fontWeight="bold"
										fontSize="sm"
										color="text.primary">
										{displayName}
									</Text>
								</Box>
								<Flex
									w={10}
									h={10}
									bg="laBlue.500"
									color="white"
									borderRadius="full"
									align="center"
									justify="center"
									fontWeight="bold"
									border="2px solid"
									borderColor="surface.panel"
									overflow="hidden"
									shadow="sm">
									{avatarUrl ? (
										<chakra.img
											src={avatarUrl}
											alt={displayName}
											w="100%"
											h="100%"
											objectFit="cover"
										/>
									) : (
										displayName.charAt(0)
									)}
								</Flex>
							</Button>
							<IconButton
								variant="ghost"
								aria-label="Sair"
								onClick={() => void signOut()}>
								<LogOut size={20} />
							</IconButton>
						</HStack>
					) : (
						<>
							<Button
								asChild
								variant="ghost"
								fontWeight="bold"
								color="text.primary">
								<RouterLink to="/login">Entrar</RouterLink>
							</Button>
							<Button
								asChild
								bg="brand.500"
								color="white"
								px={6}
								fontWeight="bold"
								_hover={{ bg: "brand.600" }}>
								<RouterLink to="/register">
									Cadastre-se
								</RouterLink>
							</Button>
						</>
					)}
				</HStack>

				{/* Mobile Menu */}
				<DrawerRoot
					placement="end"
					open={isMobileDrawerOpen}
					onOpenChange={(e) => setIsMobileDrawerOpen(e.open)}>
					<DrawerTrigger asChild>
						<IconButton
							display={{ base: "flex", lg: "none" }}
							variant="ghost"
							aria-label="Abrir menu"
							color="text.primary">
							<Menu />
						</IconButton>
					</DrawerTrigger>
					<DrawerContent bg="surface.panel">
						<DrawerHeader borderBottomWidth="1px">
							<BrandLockup compact />
						</DrawerHeader>
						<DrawerBody p={4}>
							<Stack gap={1} overflowY="auto" maxH="calc(100vh - 120px)" pr={1}>
								{isAuthenticated && (
									<Box p={3} bg="surface.muted" rounded="xl" mb={2}>
										<HStack gap={3}>
											<Flex
												w={11}
												h={11}
												bg="laBlue.500"
												color="white"
												borderRadius="full"
												align="center"
												justify="center"
												fontWeight="bold"
												fontSize="lg"
												overflow="hidden"
												flexShrink={0}>
												{avatarUrl ? (
													<chakra.img
														src={avatarUrl}
														alt={displayName}
														w="100%"
														h="100%"
														objectFit="cover"
													/>
												) : (
													displayName.charAt(0)
												)}
											</Flex>
											<Box minW={0} flex="1">
												<Text fontWeight="bold" fontSize="sm" truncate>
													{displayName}
												</Text>
												<Text fontSize="xs" color="text.muted" truncate>
													{session?.user?.email}
												</Text>
											</Box>
										</HStack>
										<Stack gap={1} mt={3} pt={2} borderTop="1px solid" borderColor="border.subtle">
											<Button
												asChild
												size="sm"
												variant="ghost"
												justifyContent="flex-start"
												onClick={() => setIsMobileDrawerOpen(false)}>
												<RouterLink to="/profile">Meu Perfil</RouterLink>
											</Button>
											{isStudent && (
												<>
													<Button
														asChild
														size="sm"
														variant="ghost"
														justifyContent="flex-start"
														onClick={() => setIsMobileDrawerOpen(false)}>
														<RouterLink to="/my-lessons">Minhas Aulas</RouterLink>
													</Button>
													<Button
														asChild
														size="sm"
														variant="ghost"
														justifyContent="flex-start"
														onClick={() => setIsMobileDrawerOpen(false)}>
														<RouterLink to="/search">Buscar Instrutores</RouterLink>
													</Button>
												</>
											)}
											{isInstructor && (
												<Button
													asChild
													size="sm"
													variant="ghost"
													justifyContent="flex-start"
													onClick={() => setIsMobileDrawerOpen(false)}>
													<RouterLink to="/instructor/dashboard">Painel do Instrutor</RouterLink>
												</Button>
											)}
											{isAdmin && (
												<Button
													asChild
													size="sm"
													variant="ghost"
													justifyContent="flex-start"
													onClick={() => setIsMobileDrawerOpen(false)}>
													<RouterLink to="/admin/instructors">Painel Administrativo</RouterLink>
												</Button>
											)}
										</Stack>
									</Box>
								)}

								<Text fontSize="2xs" fontWeight="800" color="text.muted" textTransform="uppercase" px={2} pt={2}>
									Para Alunos
								</Text>
								<Button asChild variant="ghost" justifyContent="flex-start" onClick={() => setIsMobileDrawerOpen(false)}>
									<RouterLink to="/search">Buscar Instrutores</RouterLink>
								</Button>
								<Button asChild variant="ghost" justifyContent="flex-start" onClick={() => setIsMobileDrawerOpen(false)}>
									<RouterLink to="/students/first-license">Primeira Habilitação</RouterLink>
								</Button>
								<Button asChild variant="ghost" justifyContent="flex-start" onClick={() => setIsMobileDrawerOpen(false)}>
									<RouterLink to="/students/licensed">Já Habilitados</RouterLink>
								</Button>
								<Button asChild variant="ghost" justifyContent="flex-start" onClick={() => setIsMobileDrawerOpen(false)}>
									<RouterLink to="/students/how-it-works">Como Funciona para Alunos</RouterLink>
								</Button>

								<Text fontSize="2xs" fontWeight="800" color="text.muted" textTransform="uppercase" px={2} pt={3}>
									Para Instrutores
								</Text>
								<Button asChild variant="ghost" justifyContent="flex-start" color="brand.solid" fontWeight="bold" onClick={() => setIsMobileDrawerOpen(false)}>
									<RouterLink to="/register">Cadastre-se como Instrutor</RouterLink>
								</Button>
								<Button asChild variant="ghost" justifyContent="flex-start" onClick={() => setIsMobileDrawerOpen(false)}>
									<RouterLink to="/instructors/how-it-works">Como Funciona para Instrutores</RouterLink>
								</Button>
								<Button asChild variant="ghost" justifyContent="flex-start" onClick={() => setIsMobileDrawerOpen(false)}>
									<RouterLink to="/instructors/benefits">Vantagens</RouterLink>
								</Button>
								<Button asChild variant="ghost" justifyContent="flex-start" onClick={() => setIsMobileDrawerOpen(false)}>
									<RouterLink to="/instructors/simulator">Simulador de Ganhos</RouterLink>
								</Button>

								<Text fontSize="2xs" fontWeight="800" color="text.muted" textTransform="uppercase" px={2} pt={3}>
									Institucional
								</Text>
								<Button asChild variant="ghost" justifyContent="flex-start" onClick={() => setIsMobileDrawerOpen(false)}>
									<RouterLink to="/">Explorar</RouterLink>
								</Button>
								<Button asChild variant="ghost" justifyContent="flex-start" onClick={() => setIsMobileDrawerOpen(false)}>
									<RouterLink to="/about">Sobre o LinkAuto</RouterLink>
								</Button>
								<Button asChild variant="ghost" justifyContent="flex-start" onClick={() => setIsMobileDrawerOpen(false)}>
									<RouterLink to="/contact">Contato</RouterLink>
								</Button>
								<Button asChild variant="ghost" justifyContent="flex-start" onClick={() => setIsMobileDrawerOpen(false)}>
									<RouterLink to="/help">Ajuda & FAQ</RouterLink>
								</Button>

								<Box pt={4} mt={2} borderTop="1px solid" borderColor="border.subtle">
									{isAuthenticated ? (
										<Button
											variant="ghost"
											justifyContent="flex-start"
											w="full"
											color="laStatus.cancelled"
											onClick={() => {
												setIsMobileDrawerOpen(false);
												void signOut();
											}}>
											<LogOut size={20} /> Sair
										</Button>
									) : (
										<Stack gap={2}>
											<Button asChild bg="brand.500" w="full" onClick={() => setIsMobileDrawerOpen(false)}>
												<RouterLink to="/register">Cadastre-se</RouterLink>
											</Button>
											<Button asChild variant="outline" w="full" onClick={() => setIsMobileDrawerOpen(false)}>
												<RouterLink to="/login">Entrar</RouterLink>
											</Button>
										</Stack>
									)}
								</Box>
							</Stack>
						</DrawerBody>
						<DrawerCloseTrigger />
					</DrawerContent>
				</DrawerRoot>

				{/* Profile Sidebar */}
				<ProfileSidebar
					open={isProfileOpen}
					onOpenChange={setIsProfileOpen}
				/>
			</Flex>
		</Box>
	);
}
