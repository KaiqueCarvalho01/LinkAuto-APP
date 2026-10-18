import { useCallback, useEffect, useState } from "react";
import { Box, Button, HStack, Stack, Text } from "@chakra-ui/react";
import { AlertTriangle, Calendar, Clock, MapPin } from "lucide-react";

import { bookingService } from "../services/bookingService";
import type { DashboardRequest } from "../types/session";

interface InstructorUpcomingLessonsProps {
	readonly token: string | undefined;
}

// Confirmed lessons stay visible after the instructor accepts them, and can be cancelled
export function InstructorUpcomingLessons({ token }: InstructorUpcomingLessonsProps) {
	const [lessons, setLessons] = useState<DashboardRequest[]>([]);
	const [confirmingId, setConfirmingId] = useState<string | null>(null);
	const [cancellingId, setCancellingId] = useState<string | null>(null);
	const [errorMsg, setErrorMsg] = useState<string | null>(null);

	const load = useCallback(async () => {
		if (!token) return [];
		return bookingService.getUpcomingLessons(token);
	}, [token]);

	useEffect(() => {
		let active = true;
		void load()
			.then((next) => {
				if (active) setLessons(next);
			})
			.catch((err) => {
				console.error("Failed to load upcoming lessons:", err);
				if (active) setErrorMsg("Não foi possível carregar suas próximas aulas.");
			});
		return () => {
			active = false;
		};
	}, [load]);

	const handleCancel = async (bookingId: string) => {
		if (!token) return;
		setCancellingId(bookingId);
		setErrorMsg(null);
		try {
			await bookingService.cancelBooking(bookingId, token, "Cancelado pelo instrutor");
			setConfirmingId(null);
		} catch (err) {
			console.error("Failed to cancel lesson:", err);
			setErrorMsg("Não foi possível cancelar a aula. Tente novamente.");
		}
		try {
			setLessons(await load());
		} catch (err) {
			console.error("Failed to reload upcoming lessons:", err);
		}
		setCancellingId(null);
	};

	return (
		<Stack gap={4}>
			<Text color="text.primary" fontWeight="800" fontSize="lg" fontFamily="heading" px={1}>
				Próximas aulas
			</Text>

			{errorMsg && (
				<HStack
					p={4}
					bg="red.50"
					color="red.700"
					borderRadius="xl"
					border="1px solid"
					borderColor="red.200"
					gap={2}
					role="alert">
					<AlertTriangle size={18} aria-hidden="true" />
					<Text fontSize="sm" fontWeight="600">
						{errorMsg}
					</Text>
				</HStack>
			)}

			{lessons.length === 0 ? (
				<Box
					bg="surface.panel"
					borderRadius="3xl"
					border="1px dashed"
					borderColor="border.default"
					py={10}
					px={6}
					textAlign="center">
					<Text color="text.secondary" fontWeight="700">
						Nenhuma aula confirmada por enquanto.
					</Text>
				</Box>
			) : (
				lessons.map((lesson) => (
					<Box
						key={lesson.id}
						bg="surface.panel"
						borderRadius="3xl"
						border="1px solid"
						borderColor="border.subtle"
						p={5}>
						<Stack gap={3}>
							<Text fontWeight="800" color="text.primary">
								{lesson.name}
							</Text>
							<HStack gap={4} flexWrap="wrap" color="text.secondary">
								<HStack gap={1.5}>
									<Calendar size={14} aria-hidden="true" />
									<Text fontSize="sm" fontWeight="700">
										{lesson.date}
									</Text>
								</HStack>
								<HStack gap={1.5}>
									<Clock size={14} aria-hidden="true" />
									<Text fontSize="sm" fontWeight="700">
										{lesson.time}
									</Text>
								</HStack>
								<HStack gap={1.5}>
									<MapPin size={14} aria-hidden="true" />
									<Text fontSize="sm" fontWeight="700">
										{lesson.city}
									</Text>
								</HStack>
							</HStack>
							<HStack justify="flex-end">
								{confirmingId === lesson.id ? (
									<HStack gap={2}>
										<Text fontSize="xs" color="text.muted">
											Cancelar esta aula? O aluno será avisado.
										</Text>
										<Button
											size="sm"
											colorPalette="red"
											loading={cancellingId === lesson.id}
											onClick={() => {
												void handleCancel(lesson.id);
											}}>
											Sim, cancelar
										</Button>
										<Button
											size="sm"
											variant="outline"
											disabled={cancellingId !== null}
											onClick={() => setConfirmingId(null)}>
											Não
										</Button>
									</HStack>
								) : (
									<Button
										size="sm"
										variant="ghost"
										colorPalette="red"
										disabled={cancellingId !== null}
										onClick={() => setConfirmingId(lesson.id)}>
										Cancelar aula
									</Button>
								)}
							</HStack>
						</Stack>
					</Box>
				))
			)}
		</Stack>
	);
}
