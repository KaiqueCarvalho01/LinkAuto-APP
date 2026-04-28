import {
	Box,
	Flex,
	Text,
	DrawerRoot,
	DrawerContent,
	DrawerHeader,
	DrawerBody,
	DrawerCloseTrigger,
	DrawerBackdrop,
	Stack,
	Tabs,
	Button,
	DrawerPositioner,
} from "@chakra-ui/react";
import { Link as RouterLink, useNavigate } from "react-router-dom";
import {
	LogOut,
	Calendar,
	Search,
	User as UserIcon,
	Shield,
} from "lucide-react";
import { useSessionStore } from "../state/sessionStore";

interface ProfileSidebarProps {
	open: boolean;
	onOpenChange: (open: boolean) => void;
}

export function ProfileSidebar({ open, onOpenChange }: ProfileSidebarProps) {
	const { session, signOut } = useSessionStore();
	const navigate = useNavigate();
	const user = session?.user;

	if (!user) return null;

	const displayName =
		user.student_profile?.full_name ||
		user.instructor_profile?.full_name ||
		user.email.split("@")[0] ||
		"Usuário";

	const handleLogout = () => {
		signOut();
		onOpenChange(false);
		navigate("/login");
	};

	const renderNavLinks = (role: string) => {
		if (role === "ADMIN") {
			return (
				<Stack gap={2} mt={4}>
					<Button
						asChild
						variant="ghost"
						justifyContent="flex-start"
						w="full"
						gap={3}>
						<RouterLink to="/admin/instructors">
							<Shield size={20} /> Gerenciar Instrutores
						</RouterLink>
					</Button>
					<Button
						asChild
						variant="ghost"
						justifyContent="flex-start"
						w="full"
						gap={3}>
						<RouterLink to="/profile">
							<UserIcon size={20} /> Meu Perfil
						</RouterLink>
					</Button>
				</Stack>
			);
		}

		return (
			<Stack gap={2} mt={4}>
				<Button
					asChild
					variant="ghost"
					justifyContent="flex-start"
					w="full"
					gap={3}>
					<RouterLink to="/agendamentos">
						<Calendar size={20} /> Minhas Aulas
					</RouterLink>
				</Button>
				<Button
					asChild
					variant="ghost"
					justifyContent="flex-start"
					w="full"
					gap={3}>
					<RouterLink to="/buscar">
						<Search size={20} /> Buscar Instrutor
					</RouterLink>
				</Button>
				<Button
					asChild
					variant="ghost"
					justifyContent="flex-start"
					w="full"
					gap={3}>
					<RouterLink to="/profile">
						<UserIcon size={20} /> Meu Perfil
					</RouterLink>
				</Button>
			</Stack>
		);
	};

	const activeRole = user.roles[0] || "STUDENT";

	return (
		<DrawerRoot
			placement="end"
			open={open}
			onOpenChange={(e) => onOpenChange(e.open)}>
			<DrawerBackdrop />
			<DrawerPositioner>
				<DrawerContent
					bg="surface.emphatized"
					maxW="320px"
					borderLeft="1px solid"
					borderColor="border.subtle">
					<DrawerHeader borderBottomWidth="1px" p={6}>
						<Flex gap={1} align="center">
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
							<Box overflow="hidden">
								<Text fontWeight="bold" truncate>
									{displayName}
								</Text>
								<Text fontSize="xs" color="text.muted" truncate>
									{user.email}
								</Text>
							</Box>
						</Flex>
					</DrawerHeader>

					<DrawerBody p={0}>
						{user.roles.length > 1 ? (
							<Tabs.Root
								defaultValue={user.roles[0]}
								variant="line">
								<Tabs.List px={6} borderBottomWidth="1px">
									{user.roles.map((role) => (
										<Tabs.Trigger
											key={role}
											value={role}
											fontSize="xs"
											fontWeight="bold">
											{role}
										</Tabs.Trigger>
									))}
								</Tabs.List>
								{user.roles.map((role) => (
									<Tabs.Content
										key={role}
										value={role}
										px={6}
										py={4}>
										{renderNavLinks(role)}
									</Tabs.Content>
								))}
							</Tabs.Root>
						) : (
							<Box px={6} py={6}>
								<Text
									fontSize="xs"
									fontWeight="bold"
									color="brand.600"
									mb={2}
									textTransform="uppercase">
									Role: {activeRole}
								</Text>
								{renderNavLinks(activeRole)}
							</Box>
						)}
					</DrawerBody>

					<Box p={6} borderTopWidth="1px">
						<Button
							variant="ghost"
							color="laStatus.cancelled"
							w="full"
							justifyContent="flex-start"
							gap={3}
							onClick={handleLogout}>
							<LogOut size={20} /> Sair
						</Button>
					</Box>
					<DrawerCloseTrigger />
				</DrawerContent>
			</DrawerPositioner>
		</DrawerRoot>
	);
}
