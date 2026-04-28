import {
	Box,
	Button,
	HStack,
	SimpleGrid,
	Text,
	VStack,
} from "@chakra-ui/react";

import { bookingSelectionIsValid } from "../features/bookings/bookingRules";
import type { BookingSlot } from "../types/booking";

interface SlotPickerProps {
	readonly slots: BookingSlot[];
	readonly selectedIds: string[];
	readonly onSelectedIdsChange: (nextSelectedIds: string[]) => void;
}

export function SlotPicker({
	slots,
	selectedIds,
	onSelectedIdsChange,
}: SlotPickerProps) {
	const selectedSet = new Set(selectedIds);
	const validSelection = bookingSelectionIsValid(slots, selectedIds);

	const toggleSlot = (slot: BookingSlot) => {
		if (slot.state !== "DISPONIVEL") {
			return;
		}

		if (selectedSet.has(slot.id)) {
			onSelectedIdsChange(selectedIds.filter((id) => id !== slot.id));
			return;
		}

		onSelectedIdsChange([...selectedIds, slot.id]);
	};

	return (
		<VStack align="stretch" gap={4}>
			<SimpleGrid columns={{ base: 2, md: 3 }} gap={3}>
				{slots.map((slot) => {
					const selected = selectedSet.has(slot.id);
					const disabled = slot.state !== "DISPONIVEL";

					let bg = "surface.panel";
					let color = "text.primary";
					let borderColor = "border.default";
					let hoverProps: {
						_hover?: { bg: string; borderColor?: string };
					} = {
						_hover: {
							bg: "brand.muted",
							borderColor: "brand.solid",
						},
					};

					if (disabled) {
						bg = "surface.muted";
						color = "text.muted";
						hoverProps = {};
					} else if (selected) {
						bg = "brand.solid";
						color = "text.inverse";
						borderColor = "brand.solid";
						hoverProps = { _hover: { bg: "brand.emphasized" } };
					}

					return (
						<Button
							key={slot.id}
							h="54px"
							onClick={() => toggleSlot(slot)}
							disabled={disabled}
							border="1px solid"
							borderColor={borderColor}
							bg={bg}
							color={color}
							fontWeight="700"
							borderRadius="xl"
							{...hoverProps}
							data-testid={`slot-${slot.id}`}>
							{slot.label}
						</Button>
					);
				})}
			</SimpleGrid>

			<Box>
				{selectedIds.length === 0 ? (
					<Text fontSize="sm" color="text.muted" fontWeight="500">
						Selecione no minimo 2 slots consecutivos no mesmo dia.
					</Text>
				) : null}

				{selectedIds.length > 0 && !validSelection ? (
					<HStack
						px={3}
						py={2.5}
						bg="state.warning.bg"
						borderRadius="xl"
						border="1px solid"
						borderColor="state.warning.border">
						<Text
							fontSize="sm"
							color="state.warning.fg"
							fontWeight="700">
							A reserva exige no minimo 2 horas consecutivas.
						</Text>
					</HStack>
				) : null}

				{validSelection ? (
					<HStack
						px={3}
						py={2.5}
						bg="state.success.bg"
						borderRadius="xl"
						border="1px solid"
						borderColor="state.success.border">
						<Text
							fontSize="sm"
							color="state.success.fg"
							fontWeight="700">
							Selecao valida para solicitar o agendamento.
						</Text>
					</HStack>
				) : null}
			</Box>
		</VStack>
	);
}
