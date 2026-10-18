import { useCallback, useEffect, useMemo, useState } from "react";
import { Box, Button, HStack, Input, Stack, Text, chakra } from "@chakra-ui/react";
import { AlertTriangle, CalendarPlus, Info, Trash2 } from "lucide-react";

import { formatDateLabel } from "../services/bookingService";
import { HttpClientError } from "../services/httpClient";
import { slotService } from "../services/slotService";
import type { BookingSlot } from "../types/booking";

interface InstructorAgendaProps {
	readonly token: string | undefined;
	// Slots of instructors awaiting validation are not public yet (RN01)
	readonly awaitingApproval?: boolean;
}

// Bookings need at least 2 consecutive one-hour slots, so let instructors open several at once
const FIRST_START_HOUR = 6;
const LAST_END_HOUR = 22;
const HOUR_OPTIONS = Array.from(
	{ length: LAST_END_HOUR - FIRST_START_HOUR },
	(_, index) => index + FIRST_START_HOUR,
);
const MAX_CONSECUTIVE_HOURS = 6;

const pad = (value: number) => String(value).padStart(2, "0");

// The app stores and shows slot times on the UTC clock (see formatSlotLabel), so a slot
// opened at "09:00" on a date is 09:00Z
export const buildSlotTimes = (date: string, startHour: number, hours: number) =>
	Array.from({ length: hours }, (_, index) => {
		const hour = startHour + index;
		return {
			starts_at: `${date}T${pad(hour)}:00:00Z`,
			ends_at: `${date}T${pad(hour + 1)}:00:00Z`,
		};
	});

const describeError = (err: unknown): string => {
	if (err instanceof HttpClientError) {
		if (err.status === 409) return "Já existe um horário seu nesse período.";
		if (err.status === 422) return "Escolha um horário no futuro.";
	}
	return "Não foi possível salvar o horário. Tente novamente.";
};

const STATUS_LABELS: Record<string, string> = {
	DISPONIVEL: "Disponível",
	RESERVADO: "Reservado",
};

export function InstructorAgenda({ token, awaitingApproval = false }: InstructorAgendaProps) {
	const [slots, setSlots] = useState<BookingSlot[]>([]);
	const [date, setDate] = useState("");
	const [startHour, setStartHour] = useState(8);
	const [hours, setHours] = useState(2);
	const [saving, setSaving] = useState(false);
	const [removingId, setRemovingId] = useState<string | null>(null);
	const [errorMsg, setErrorMsg] = useState<string | null>(null);

	// Past slots are history: only upcoming ones are shown
	const load = useCallback(async () => {
		if (!token) return [];
		const now = Date.now();
		return (await slotService.getMySlots(token)).filter(
			(slot) => new Date(slot.startAt).getTime() > now,
		);
	}, [token]);

	useEffect(() => {
		let active = true;
		void load()
			.then((next) => {
				if (active) setSlots(next);
			})
			.catch((err) => {
				console.error("Failed to load agenda:", err);
				if (active) setErrorMsg("Não foi possível carregar sua agenda.");
			});
		return () => {
			active = false;
		};
	}, [load]);

	const reload = async () => {
		try {
			setSlots(await load());
		} catch (err) {
			console.error("Failed to reload agenda:", err);
		}
	};

	const upcomingByDay = useMemo(() => {
		const groups = new Map<string, BookingSlot[]>();
		for (const slot of slots) {
			const day = formatDateLabel(slot.startAt);
			groups.set(day, [...(groups.get(day) ?? []), slot]);
		}
		return [...groups.entries()];
	}, [slots]);

	const lastHour = Math.min(startHour + hours, LAST_END_HOUR);

	const handleAdd = async (e: React.FormEvent) => {
		e.preventDefault();
		if (!token || !date) return;
		setSaving(true);
		setErrorMsg(null);
		const failures: string[] = [];
		for (const times of buildSlotTimes(date, startHour, lastHour - startHour)) {
			try {
				await slotService.createSlot(times, token);
			} catch (err) {
				failures.push(describeError(err));
			}
		}
		if (failures.length > 0) {
			setErrorMsg([...new Set(failures)].join(" "));
		}
		await reload();
		setSaving(false);
	};

	const handleRemove = async (slotId: string) => {
		if (!token) return;
		setRemovingId(slotId);
		setErrorMsg(null);
		try {
			await slotService.deleteSlot(slotId, token);
		} catch (err) {
			console.error("Failed to remove slot:", err);
			setErrorMsg("Não foi possível remover o horário. Ele pode ter sido reservado.");
		}
		await reload();
		setRemovingId(null);
	};

	return (
		<Stack gap={4}>
			<Text color="text.primary" fontWeight="800" fontSize="lg" fontFamily="heading" px={1}>
				Minha agenda
			</Text>

			{awaitingApproval && (
				<HStack
					p={4}
					bg="state.warning.bg"
					color="state.warning.fg"
					borderRadius="xl"
					border="1px solid"
					borderColor="state.warning.border"
					gap={2}>
					<Info size={18} aria-hidden="true" />
					<Text fontSize="sm" fontWeight="600">
						Seus horários ficam visíveis para os alunos depois que seu credenciamento for
						aprovado.
					</Text>
				</HStack>
			)}

			<Box
				as="form"
				onSubmit={handleAdd}
				bg="surface.panel"
				borderRadius="3xl"
				border="1px solid"
				borderColor="border.subtle"
				p={5}>
				<Stack gap={4}>
					<HStack gap={3} flexWrap="wrap" align="end">
						<Box flex="1" minW="160px">
							<Text asChild display="block" fontSize="xs" fontWeight="700" mb={1.5} color="text.secondary">
								<label htmlFor="agenda-date">Dia</label>
							</Text>
							<Input
								id="agenda-date"
								type="date"
								required
								value={date}
								onChange={(e) => setDate(e.target.value)}
								bg="surface.canvas"
								borderRadius="xl"
							/>
						</Box>
						<Box minW="120px">
							<Text asChild display="block" fontSize="xs" fontWeight="700" mb={1.5} color="text.secondary">
								<label htmlFor="agenda-start">Início</label>
							</Text>
							<chakra.select
								id="agenda-start"
								value={startHour}
								onChange={(e) => setStartHour(Number(e.target.value))}
								h="40px"
								px={3}
								bg="surface.canvas"
								borderRadius="xl"
								border="1px solid"
								borderColor="border.default">
								{HOUR_OPTIONS.map((hour) => (
									<option key={hour} value={hour}>
										{pad(hour)}:00
									</option>
								))}
							</chakra.select>
						</Box>
						<Box minW="120px">
							<Text asChild display="block" fontSize="xs" fontWeight="700" mb={1.5} color="text.secondary">
								<label htmlFor="agenda-hours">Horas seguidas</label>
							</Text>
							<chakra.select
								id="agenda-hours"
								value={hours}
								onChange={(e) => setHours(Number(e.target.value))}
								h="40px"
								px={3}
								bg="surface.canvas"
								borderRadius="xl"
								border="1px solid"
								borderColor="border.default">
								{Array.from({ length: MAX_CONSECUTIVE_HOURS }, (_, index) => index + 1).map(
									(count) => (
										<option key={count} value={count}>
											{count}
										</option>
									),
								)}
							</chakra.select>
						</Box>
						<Button
							type="submit"
							loading={saving}
							bg="brand.solid"
							color="text.inverse"
							borderRadius="xl"
							_hover={{ bg: "brand.emphasized" }}>
							<CalendarPlus size={16} aria-hidden="true" />
							Abrir horários
						</Button>
					</HStack>
					<Text fontSize="xs" color="text.muted">
						Abre {lastHour - startHour} horário(s) de 1 hora, das {pad(startHour)}:00 às{" "}
						{pad(lastHour)}:00. Os alunos reservam no mínimo 2 horários seguidos.
					</Text>
				</Stack>
			</Box>

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

			{upcomingByDay.length === 0 ? (
				<Box
					bg="surface.panel"
					borderRadius="3xl"
					border="1px dashed"
					borderColor="border.default"
					py={10}
					px={6}
					textAlign="center">
					<Text color="text.secondary" fontWeight="700">
						Nenhum horário futuro na sua agenda.
					</Text>
				</Box>
			) : (
				upcomingByDay.map(([day, daySlots]) => (
					<Box
						key={day}
						bg="surface.panel"
						borderRadius="3xl"
						border="1px solid"
						borderColor="border.subtle"
						p={5}>
						<Text fontWeight="800" color="text.primary" mb={3}>
							{day}
						</Text>
						<Stack gap={2}>
							{daySlots.map((slot) => (
								<HStack key={slot.id} justify="space-between">
									<HStack gap={3}>
										<Text fontWeight="700" color="text.secondary">
											{slot.label}
										</Text>
										<Text fontSize="xs" fontWeight="700" color="text.muted">
											{STATUS_LABELS[slot.state] ?? slot.state}
										</Text>
									</HStack>
									{slot.state === "DISPONIVEL" && (
										<Button
											size="sm"
											variant="ghost"
											colorPalette="red"
											aria-label={`Remover horário ${day} ${slot.label}`}
											loading={removingId === slot.id}
											disabled={removingId !== null}
											onClick={() => {
												void handleRemove(slot.id);
											}}>
											<Trash2 size={16} aria-hidden="true" />
										</Button>
									)}
								</HStack>
							))}
						</Stack>
					</Box>
				))
			)}
		</Stack>
	);
}
