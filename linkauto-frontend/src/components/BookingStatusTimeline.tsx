import { Box, Circle, HStack, Text, VStack } from "@chakra-ui/react";

import { BookingStatusBadge } from "./BookingStatusBadge";
import type { BookingStatus } from "../types/booking";

interface BookingStatusTimelineProps {
	readonly status: BookingStatus;
}

const flow: BookingStatus[] = ["PENDENTE", "CONFIRMADA", "REALIZADA"];

const labelByStatus: Record<BookingStatus, string> = {
	PENDENTE: "Pendente",
	CONFIRMADA: "Confirmada",
	REALIZADA: "Realizada",
	CANCELADA: "Cancelada",
};

export function BookingStatusTimeline({ status }: BookingStatusTimelineProps) {
	const cancelado = status === "CANCELADA";
	const resolvedStatus = cancelado ? "PENDENTE" : status;
	const currentIndex = flow.indexOf(resolvedStatus);

	return (
		<VStack align="stretch" gap={3}>
			<HStack align="start" gap={0}>
				{flow.map((step, index) => {
					const completed = !cancelado && index < currentIndex;
					const current = !cancelado && index === currentIndex;
					return (
						<HStack
							key={step}
							flex={index === flow.length - 1 ? "0 0 auto" : "1"}
							gap={0}
							align="center">
							<VStack align="center" gap={2} minW="84px">
								<Circle
									size="30px"
									fontSize="xs"
									fontWeight="700"
									bg={
										current || completed
											? "brand.solid"
											: "surface.muted"
									}
									border="1px solid"
									borderColor={
										current || completed
											? "brand.solid"
											: "border.default"
									}
									color={
										current || completed
											? "text.inverse"
											: "text.muted"
									}>
									{index + 1}
								</Circle>
								<Text
									fontSize="xs"
									fontWeight={current ? "700" : "600"}
									color={
										current
											? "brand.emphasized"
											: "text.muted"
									}
									textAlign="center">
									{labelByStatus[step]}
								</Text>
							</VStack>
							{index < flow.length - 1 ? (
								<Box
									flex="1"
									h="2px"
									mx={2}
									bg={
										completed
											? "brand.solid"
											: "border.default"
									}
								/>
							) : null}
						</HStack>
					);
				})}
			</HStack>
			{cancelado ? (
				<HStack justify="flex-start">
					<BookingStatusBadge status="CANCELADA" />
				</HStack>
			) : null}
		</VStack>
	);
}
