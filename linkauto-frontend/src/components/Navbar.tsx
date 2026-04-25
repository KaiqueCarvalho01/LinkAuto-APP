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
	MenuPositioner,
	Text,
	PopoverRoot,
	PopoverTrigger,
	PopoverContent,
	PopoverBody,
	PopoverHeader,
	PopoverFooter,
	Link,
	DrawerRoot,
	DrawerTrigger,
	DrawerContent,
	DrawerHeader,
	DrawerBody,
	DrawerCloseTrigger,
	Stack,
	PopoverPositioner,
} from "@chakra-ui/react";
import { Link as RouterLink } from "react-router-dom";
import { Menu, ChevronDown, Bell, LogOut } from "lucide-react";
import { BrandLockup } from "./BrandLockup";
import { useState, useEffect } from "react";
import { useSessionStore } from "../state/sessionStore";
import { ProfileSidebar } from "./ProfileSidebar";

export function Navbar() {
	const [scrolled, setScrolled] = useState(false);
	const [isProfileOpen, setIsProfileOpen] = useState(false);
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

	// Mock notifications for FE-002
	const notifications = [
		{
			id: 1,
			text: "Sua aula com Marcos foi confirmada.",
			time: "2h atrás",
		},
		{
			id: 2,
			text: "Novo instrutor disponível na sua área.",
			time: "5h atrás",
		},
	];

	const user = session?.user;
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
									<RouterLink to="/instructors/register">
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
							<PopoverRoot>
								<PopoverTrigger asChild>
									<IconButton
										variant="ghost"
										aria-label="Notificações"
										position="relative">
										<Bell size={20} />
										<Box
											position="absolute"
											top="2"
											right="2"
											w="2"
											h="2"
											bg="laStatus.cancelled"
											borderRadius="full"
											border="2px solid"
											borderColor="surface.panel"
										/>
									</IconButton>
								</PopoverTrigger>
								<PopoverPositioner>
									<PopoverContent
										rounded="xl"
										shadow="xl"
										border="1px solid"
										borderColor="border.subtle"
										bg="surface.panel">
										<PopoverHeader
											fontWeight="bold"
											p={4}
											borderBottom="1px solid"
											borderColor="border.subtle">
											Notificações
										</PopoverHeader>
										<PopoverBody p={0}>
											<Stack gap={0}>
												{notifications.map((n) => (
													<Box
														key={n.id}
														p={4}
														_hover={{
															bg: "surface.muted",
														}}
														borderBottom="1px solid"
														borderColor="border.subtle"
														cursor="pointer">
														<Text fontSize="sm">
															{n.text}
														</Text>
														<Text
															fontSize="xs"
															color="text.muted"
															mt={1}>
															{n.time}
														</Text>
													</Box>
												))}
											</Stack>
										</PopoverBody>
										<PopoverFooter p={3} textAlign="center">
											<Link
												asChild
												fontSize="sm"
												fontWeight="bold"
												color="brand.500">
												<RouterLink to="/notifications">
													Ver todas as notificações
												</RouterLink>
											</Link>
										</PopoverFooter>
									</PopoverContent>
								</PopoverPositioner>
							</PopoverRoot>

							<HStack
								gap={3}
								cursor="pointer"
								onClick={handleAvatarClick}
								role="button"
								aria-label="Menu de Perfil">
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
									shadow="sm">
									{displayName.charAt(0)}
								</Flex>
							</HStack>
							<IconButton
								variant="ghost"
								aria-label="Sair"
								onClick={signOut}>
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
				<DrawerRoot placement="end">
					<DrawerTrigger asChild>
						<IconButton
							display={{ base: "flex", lg: "none" }}
							variant="ghost"
							aria-label="Open menu"
							color="text.primary">
							<Menu />
						</IconButton>
					</DrawerTrigger>
					<DrawerContent bg="surface.panel">
						<DrawerHeader borderBottomWidth="1px">
							<BrandLockup compact />
						</DrawerHeader>
						<DrawerBody p={4}>
							<Stack gap={4}>
								{isAuthenticated && (
									<HStack
										p={4}
										bg="surface.muted"
										rounded="xl"
										gap={4}>
										<Flex
											w={12}
											h={12}
											bg="laBlue.500"
											color="white"
											borderRadius="full"
											align="center"
											justify="center"
											fontWeight="bold"
											fontSize="xl">
											{displayName.charAt(0)}
										</Flex>
										<Box>
											<Text fontWeight="bold">
												{displayName}
											</Text>
											<Text
												fontSize="xs"
												color="text.muted">
												{session?.user?.email}
											</Text>
										</Box>
									</HStack>
								)}

								<Button
									asChild
									variant="ghost"
									justifyContent="flex-start"
									w="full">
									<RouterLink to="/">Explorar</RouterLink>
								</Button>
								<Button
									asChild
									variant="ghost"
									justifyContent="flex-start"
									w="full">
									<RouterLink to="/about">Sobre</RouterLink>
								</Button>

								{isAuthenticated ? (
									<>
										<Button
											asChild
											variant="ghost"
											justifyContent="flex-start"
											w="full">
											<RouterLink to="/notifications">
												Notificações
											</RouterLink>
										</Button>
										<Button
											variant="ghost"
											justifyContent="flex-start"
											w="full"
											color="laStatus.cancelled"
											onClick={signOut}>
											<LogOut size={20} /> Sair
										</Button>
									</>
								) : (
									<Stack gap={2} mt={4}>
										<Button asChild bg="brand.500" w="full">
											<RouterLink to="/register">
												Cadastre-se
											</RouterLink>
										</Button>
										<Button
											asChild
											variant="outline"
											w="full">
											<RouterLink to="/login">
												Entrar
											</RouterLink>
										</Button>
									</Stack>
								)}
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
