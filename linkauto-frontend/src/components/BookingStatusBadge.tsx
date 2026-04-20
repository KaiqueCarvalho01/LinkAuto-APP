import {
	CheckCheck,
	CheckCircle2,
	Clock3,
	XCircle,
	type LucideIcon,
} from "lucide-react";
import { HStack, Text } from "@chakra-ui/react";

import type { BookingStatus } from "../types/booking";

interface BookingStatusBadgeProps {
	readonly status: BookingStatus;
}

interface StatusConfig {
	readonly label: string;
	readonly background: string;
	readonly color: string;
	readonly icon: LucideIcon;
}

const statusMap: Record<BookingStatus, StatusConfig> = {
	PENDENTE: {
		label: "Pendente",
		background: "state.warning.bg",
		color: "state.warning.fg",
		icon: Clock3,
	},
	CONFIRMADA: {
		label: "Confirmada",
		background: "brand.muted",
		color: "brand.emphasized",
		icon: CheckCircle2,
	},
	REALIZADA: {
		label: "Realizada",
		background: "state.success.bg",
		color: "state.success.fg",
		icon: CheckCheck,
	},
	CANCELADA: {
		label: "Cancelada",
		background: "state.danger.bg",
		color: "state.danger.fg",
		icon: XCircle,
	},
};

export const bookingStatusLabel = (status: BookingStatus): string =>
	statusMap[status].label;

export function BookingStatusBadge({ status }: BookingStatusBadgeProps) {
	const config = statusMap[status];
	const Icon = config.icon;

	return (
		<HStack
			px={3}
			py={1}
			borderRadius="full"
			bg={config.background}
			color={config.color}
			gap={1.5}
			align="center"
			aria-label={`Status ${config.label}`}>
			<Icon size={14} aria-hidden="true" />
			<Text fontSize="xs" fontWeight="700" letterSpacing="0.03em">
				{config.label}
			</Text>
		</HStack>
	);
}
