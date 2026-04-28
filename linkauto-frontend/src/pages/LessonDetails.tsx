import { useState } from "react";
import { ArrowLeft, Calendar, Clock3, TriangleAlert } from "lucide-react";
import {
	Box,
	Button,
	Container,
	Heading,
	HStack,
	Stack,
	Text,
} from "@chakra-ui/react";

import { BookingStatusTimeline } from "../components/BookingStatusTimeline";
import { RatingStars } from "../components/RatingStars";
import { SlotPicker } from "../components/SlotPicker";
import { bookingSelectionIsValid } from "../features/bookings/bookingRules";
import {
	getMockSlotsByInstructor,
	mockInstructors,
} from "../services/mockData";
import type { InstructorSummary } from "../types/instructor";

interface LessonDetailsProps {
	readonly instructor: InstructorSummary | undefined;
	readonly blockedUntil?: string | null;
	readonly onBack: () => void;
	readonly onBookingCreated: (payload: {
		instructorId: string;
		slotIds: string[];
	}) => void;
}

export default function LessonDetails({
	instructor,
	blockedUntil = null,
	onBack,
	onBookingCreated,
}: LessonDetailsProps) {
	const fallbackInstructor = mockInstructors.find(Boolean);
	const targetInstructor = instructor ?? fallbackInstructor ?? null;
	const [selectedSlotIds, setSelectedSlotIds] = useState<string[]>([]);
	const slots = targetInstructor
		? getMockSlotsByInstructor(targetInstructor.id)
		: [];
	const canCreateBooking = targetInstructor
		? bookingSelectionIsValid(slots, selectedSlotIds)
		: false;

	if (!targetInstructor) {
		return null;
	}

	return (
		<Stack minH="100vh" pb={12}>
			<Container maxW="4xl" pt={8}>
				<Stack gap={6}>
					<Button
						alignSelf="flex-start"
						variant="ghost"
						onClick={onBack}
						color="text.secondary">
						<ArrowLeft size={16} />
						Voltar para busca
					</Button>

					<Box
						bg="surface.panel"
						border="1px solid"
						borderColor="border.default"
						borderRadius="2xl"
						p={{ base: 5, md: 6 }}>
						<Stack gap={3.5}>
							<Heading
								fontSize={{ base: "2xl", md: "3xl" }}
								color="text.primary">
								Solicitar agendamento
							</Heading>
							<Text color="text.muted">
								Selecione pelo menos 2 slots consecutivos para
								montar sua aula com o instrutor.
							</Text>

							<Stack
								gap={2}
								bg="brand.muted"
								border="1px solid"
								borderColor="brand.solid"
								borderRadius="xl"
								px={4}
								py={3}>
								<Text fontWeight="700" color="brand.emphasized">
									{targetInstructor.fullName}
								</Text>
								<RatingStars
									rating={targetInstructor.rating}
									reviewsCount={targetInstructor.reviewsCount}
								/>
								<HStack
									color="text.secondary"
									fontSize="sm"
									fontWeight="600"
									gap={4}>
									<HStack gap={1.5}>
										<Calendar
											size={14}
											aria-hidden="true"
										/>
										<Text>22/05/2026</Text>
									</HStack>
									<HStack gap={1.5}>
										<Clock3 size={14} aria-hidden="true" />
										<Text>{targetInstructor.city}</Text>
									</HStack>
								</HStack>
							</Stack>
						</Stack>
					</Box>

					{blockedUntil ? (
						<HStack
							borderRadius="xl"
							bg="state.danger.bg"
							border="1px solid"
							borderColor="state.danger.border"
							align="start"
							px={4}
							py={3}
							gap={3}>
							<TriangleAlert
								size={18}
								color="currentColor"
								aria-hidden="true"
							/>
							<Text
								color="state.danger.fg"
								fontSize="sm"
								fontWeight="600">
								Sua conta esta com reservas bloqueadas ate{" "}
								{blockedUntil}. Cancelamentos com menos de 24h
								geram bloqueio de 7 dias.
							</Text>
						</HStack>
					) : null}

					<Box
						bg="surface.panel"
						border="1px solid"
						borderColor="border.default"
						borderRadius="2xl"
						p={{ base: 5, md: 6 }}>
						<Stack gap={5}>
							<Stack gap={1}>
								<Heading fontSize="xl" color="text.primary">
									Selecione os horarios
								</Heading>
								<Text color="text.muted">
									Slots reservados ou bloqueados ficam
									indisponiveis para selecao.
								</Text>
							</Stack>

							<SlotPicker
								slots={slots}
								selectedIds={selectedSlotIds}
								onSelectedIdsChange={setSelectedSlotIds}
							/>

							<HStack
								justify="space-between"
								bg="surface.muted"
								border="1px solid"
								borderColor="border.subtle"
								borderRadius="xl"
								px={4}
								py={3}>
								<HStack gap={2} color="text.muted">
									<TriangleAlert
										size={16}
										aria-hidden="true"
									/>
									<Text fontSize="sm" fontWeight="600">
										Status inicial da reserva: Pendente
									</Text>
								</HStack>
								<Text
									fontSize="sm"
									color="text.secondary"
									fontWeight="700">
									{selectedSlotIds.length} slot(s)
									selecionado(s)
								</Text>
							</HStack>

							<BookingStatusTimeline status="PENDENTE" />

							<HStack justify="flex-end" gap={3}>
								<Button
									variant="outline"
									borderColor="border.default"
									color="text.secondary"
									onClick={onBack}>
									Cancelar
								</Button>
								<Button
									disabled={
										!canCreateBooking ||
										Boolean(blockedUntil)
									}
									bg="brand.solid"
									color="text.inverse"
									_hover={{ bg: "brand.emphasized" }}
									onClick={() =>
										onBookingCreated({
											instructorId: targetInstructor.id,
											slotIds: selectedSlotIds,
										})
									}>
									Solicitar agendamento
								</Button>
							</HStack>
						</Stack>
					</Box>
				</Stack>
			</Container>
		</Stack>
	);
}
