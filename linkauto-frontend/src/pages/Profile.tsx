import {
	Bell,
	Car,
	Compass,
	ChevronRight,
	CreditCard,
	CalendarClock,
	LogOut,
	Shield,
	User,
	type LucideIcon,
} from "lucide-react";
import { Box, Button, HStack, Stack, Text } from "@chakra-ui/react";

import type { ProfileUserData } from "../types/session";

interface ProfileProps {
	readonly userData?: ProfileUserData;
	readonly onLogout: () => void;
	readonly onNavigateToSearch: () => void;
	readonly onNavigateToBookings: () => void;
	readonly onNavigateToVehicles: () => void;
}

interface MenuItem {
	readonly id: string;
	readonly icon: LucideIcon;
	readonly label: string;
	readonly iconColor: string;
	readonly action?: () => void;
}

const roleLabels: Record<ProfileUserData["role"], string> = {
	admin: "Administrador",
	instructor: "Instrutor",
	student: "Aluno",
};

export default function Profile({
	userData,
	onLogout,
	onNavigateToSearch,
	onNavigateToBookings,
	onNavigateToVehicles,
}: ProfileProps) {
	const resolvedUser: ProfileUserData = userData ?? {
		name: "Conta LinkAuto",
		email: "usuario@linkauto.app",
		role: "student",
	};

	const menuItems: MenuItem[] = [
		{
			id: "search",
			icon: Compass,
			label: "Buscar instrutores",
			iconColor: "brand.600",
			action: onNavigateToSearch,
		},
		{
			id: "bookings",
			icon: CalendarClock,
			label: "Meus agendamentos",
			iconColor: "brand.700",
			action: onNavigateToBookings,
		},
		...(resolvedUser.role === "instructor"
			? [
					{
						id: "vehicles",
						icon: Car,
						label: "Meus Veiculos",
						iconColor: "accent.600",
						action: onNavigateToVehicles,
					},
				]
			: []),
		{
			id: "notifications",
			icon: Bell,
			label: "Notificacoes",
			iconColor: "laBlue.600",
		},
		{
			id: "security",
			icon: Shield,
			label: "Seguranca e senha",
			iconColor: "laBlue.700",
		},
		{
			id: "plans",
			icon: CreditCard,
			label: "Planos e assinaturas",
			iconColor: "text.secondary",
		},
	];

	return (
		<Stack
			minH="100vh"
			px={{ base: 4, md: 8 }}
			py={{ base: 6, md: 8 }}
			gap={6}>
			<Box
				position="relative"
				overflow="hidden"
				borderRadius="3xl"
				p={{ base: 6, md: 8 }}
				bgGradient="linear(140deg, #0f2f47 0%, #1f5b86 52%, #338640 100%)"
				boxShadow="0 24px 56px rgba(19, 62, 93, 0.26)">
				<Box
					position="absolute"
					w="180px"
					h="180px"
					right="-42px"
					top="-42px"
					borderRadius="full"
					bg="whiteAlpha.200"
					filter="blur(2px)"
				/>

				<HStack align="center" gap={4} position="relative" zIndex={1}>
					<Box
						w="72px"
						h="72px"
						borderRadius="2xl"
						display="grid"
						placeItems="center"
						bg="whiteAlpha.250"
						border="1px solid"
						borderColor="text-foreground">
						<User size={26} className="text-foreground" />
					</Box>
					<Stack gap={1}>
						<Text
							color="text.primary"
							fontFamily="heading"
							fontSize={{ base: "xl", md: "2xl" }}
							fontWeight="800">
							{resolvedUser.name}
						</Text>
						<Text color="text.muted" fontWeight="600" fontSize="sm">
							{resolvedUser.email}
						</Text>
						<Box
							mt={1}
							alignSelf="start"
							px={3}
							py={1}
							borderRadius="full"
							bg="whiteAlpha.250"
							border="1px solid"
							borderColor="border.emphasized">
							<Text
								color="text.muted"
								fontSize="2xs"
								fontWeight="800"
								letterSpacing="0.14em"
								textTransform="uppercase">
								Conta {roleLabels[resolvedUser.role]}
							</Text>
						</Box>
					</Stack>
				</HStack>
			</Box>

			<Box
				bg="surface.panel"
				borderRadius="3xl"
				p={3}
				border="1px solid"
				borderColor="border.subtle">
				<Stack gap={1}>
					{menuItems.map((item) => {
						const ItemIcon = item.icon;
						return (
							<Button
								key={item.id}
								onClick={item.action}
								justifyContent="space-between"
								variant="ghost"
								h="58px"
								borderRadius="2xl"
								px={3.5}
								_hover={{ bg: "surface.muted" }}>
								<HStack align="center" gap={3}>
									<Box
										w="36px"
										h="36px"
										display="grid"
										placeItems="center"
										bg="surface.muted"
										borderRadius="xl"
										color={item.iconColor}>
										<ItemIcon size={18} />
									</Box>
									<Text color="text.primary" fontWeight="700">
										{item.label}
									</Text>
								</HStack>
								<ChevronRight
									size={16}
									color="var(--chakra-colors-text-muted)"
								/>
							</Button>
						);
					})}
				</Stack>
			</Box>

			<Button
				onClick={onLogout}
				h="56px"
				borderRadius="2xl"
				bg="state.danger.bg"
				color="state.danger.fg"
				border="1px solid"
				borderColor="state.danger.border"
				fontWeight="800"
				gap={2}
				_hover={{ filter: "brightness(0.95)" }}>
				<LogOut size={18} />
				Sair da conta
			</Button>

			<Text
				textAlign="center"
				color="text.muted"
				fontSize="xs"
				fontWeight="600"
				letterSpacing="0.08em">
				Fatec Mogi Mirim • ADS • 2026
			</Text>
		</Stack>
	);
}
