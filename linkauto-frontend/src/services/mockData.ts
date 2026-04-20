import type { BookingPreview, BookingSlot } from "../types/booking";
import type { InstructorSummary } from "../types/instructor";

export const mockInstructors: InstructorSummary[] = [
	{
		id: "instr-001",
		fullName: "Camila Rocha",
		city: "Mogi Mirim",
		neighborhood: "Centro",
		rating: 4.8,
		reviewsCount: 96,
		distanceKm: 2.4,
		hourlyRate: 85,
		detranApproved: true,
		specialties: ["Primeira habilitacao", "Baliza"],
		radiusKm: 7,
		coordinates: {
			lat: -22.4331,
			lng: -46.957,
		},
	},
	{
		id: "instr-002",
		fullName: "Rafael Mendes",
		city: "Mogi Mirim",
		neighborhood: "Parque da Imprensa",
		rating: 4.6,
		reviewsCount: 58,
		distanceKm: 5.1,
		hourlyRate: 92,
		detranApproved: true,
		specialties: ["Reciclagem", "Direcao defensiva"],
		radiusKm: 10,
		coordinates: {
			lat: -22.4174,
			lng: -46.95,
		},
	},
	{
		id: "instr-003",
		fullName: "Fernanda Siqueira",
		city: "Mogi Guaçu",
		neighborhood: "Jardim Ipe",
		rating: 4.7,
		reviewsCount: 74,
		distanceKm: 8.8,
		hourlyRate: 88,
		detranApproved: true,
		specialties: ["Aulas noturnas", "Primeira habilitacao"],
		radiusKm: 12,
		coordinates: {
			lat: -22.3732,
			lng: -46.9436,
		},
	},
];

const [primaryInstructor, secondaryInstructor, tertiaryInstructor] =
	mockInstructors;

if (!primaryInstructor || !secondaryInstructor || !tertiaryInstructor) {
	throw new Error("Mock instructors were not initialized correctly.");
}

const slotHourLabels = [
	"08:00",
	"09:00",
	"10:00",
	"11:00",
	"13:00",
	"14:00",
	"15:00",
	"16:00",
];

const slotStatesByInstructor: Record<string, BookingSlot["state"][]> = {
	"instr-001": [
		"DISPONIVEL",
		"DISPONIVEL",
		"RESERVADO",
		"DISPONIVEL",
		"DISPONIVEL",
		"DISPONIVEL",
		"BLOQUEADO",
		"DISPONIVEL",
	],
	"instr-002": [
		"DISPONIVEL",
		"DISPONIVEL",
		"DISPONIVEL",
		"DISPONIVEL",
		"RESERVADO",
		"DISPONIVEL",
		"DISPONIVEL",
		"DISPONIVEL",
	],
	"instr-003": [
		"BLOQUEADO",
		"DISPONIVEL",
		"DISPONIVEL",
		"DISPONIVEL",
		"DISPONIVEL",
		"RESERVADO",
		"DISPONIVEL",
		"DISPONIVEL",
	],
};

export const getMockSlotsByInstructor = (
	instructorId: string,
): BookingSlot[] => {
	const day = "2026-05-22";
	const fallbackStates = slotStatesByInstructor["instr-001"] ?? [];
	const states = slotStatesByInstructor[instructorId] ?? fallbackStates;

	return slotHourLabels.map((hour, index) => {
		const [hourPart = "00", minutePart = "00"] = hour.split(":");
		const startHour = Number.parseInt(hourPart, 10);
		const endHour = startHour + 1;
		const nextLabel = `${String(endHour).padStart(2, "0")}:${minutePart}`;
		return {
			id: `${instructorId}-slot-${index}`,
			label: `${hour} - ${nextLabel}`,
			startAt: `${day}T${hour}:00.000Z`,
			endAt: `${day}T${nextLabel}:00.000Z`,
			state: states[index] ?? "DISPONIVEL",
		};
	});
};

export const mockBookings: BookingPreview[] = [
	{
		id: "book-001",
		instructor: primaryInstructor,
		dateLabel: "22/05/2026",
		timeLabel: "08:00 - 10:00",
		status: "PENDENTE",
	},
	{
		id: "book-002",
		instructor: secondaryInstructor,
		dateLabel: "18/05/2026",
		timeLabel: "14:00 - 16:00",
		status: "CONFIRMADA",
	},
	{
		id: "book-003",
		instructor: tertiaryInstructor,
		dateLabel: "10/05/2026",
		timeLabel: "10:00 - 12:00",
		status: "REALIZADA",
	},
];
