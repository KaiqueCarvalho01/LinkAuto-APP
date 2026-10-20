import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import LessonDetails from "./LessonDetails";
import { getMockSlotsByInstructor } from "../test/fixtures/mockData";
import { renderWithProviders } from "../test/renderWithProviders";
import { slotService } from "../services/slotService";
import { bookingService } from "../services/bookingService";
import { profileService } from "../services/profileService";
import type { BookingPreview } from "../types/booking";

const SLUG = "marcos-lima-mogi-mirim-4a9b";

describe("LessonDetails", () => {
	beforeEach(() => {
		vi.restoreAllMocks();
	});

	it("loads the instructor by slug and books valid slots", async () => {
		const onBookingCreated = vi.fn();
		const user = userEvent.setup();

		const fetchProfile = vi
			.spyOn(profileService, "fetchPublicInstructorProfile")
			.mockResolvedValue({
				id: SLUG,
				slug: SLUG,
				full_name: "Marcos Lima",
				city: "Mogi Mirim",
				state: "SP",
				specialties: [],
				rating_avg: 4.9,
				rating_count: 8,
				detran_approved: true,
				reviews: [],
			});
		const getSlots = vi
			.spyOn(slotService, "getInstructorSlots")
			.mockResolvedValue(getMockSlotsByInstructor("instr-001"));
		const createBooking = vi
			.spyOn(bookingService, "createBooking")
			.mockResolvedValue({} as BookingPreview);

		renderWithProviders(
			<LessonDetails
				instructorSlug={SLUG}
				onBack={vi.fn()}
				onBookingCreated={onBookingCreated}
				token="mock-token"
			/>,
		);

		expect(await screen.findByText("Marcos Lima")).toBeInTheDocument();
		expect(fetchProfile).toHaveBeenCalledWith(SLUG);
		expect(getSlots).toHaveBeenCalledWith(SLUG);

		const submitButton = screen.getByRole("button", {
			name: "Solicitar agendamento",
		});
		expect(submitButton).toBeDisabled();

		await user.click(await screen.findByTestId("slot-instr-001-slot-0"));
		expect(submitButton).toBeDisabled();

		await user.click(await screen.findByTestId("slot-instr-001-slot-1"));
		expect(submitButton).toBeEnabled();

		await user.click(submitButton);

		await vi.waitFor(() => {
			expect(onBookingCreated).toHaveBeenCalled();
		});
		expect(createBooking).toHaveBeenCalledWith(
			expect.objectContaining({ instructor_id: SLUG }),
			"mock-token",
		);
	});

	it("explains when the instructor can't be booked and offers a way back", async () => {
		const onBack = vi.fn();
		const user = userEvent.setup();
		vi.spyOn(profileService, "fetchPublicInstructorProfile").mockRejectedValue(
			new Error("Not found"),
		);
		const getSlots = vi.spyOn(slotService, "getInstructorSlots");

		renderWithProviders(
			<LessonDetails
				instructorSlug="sumiu"
				onBack={onBack}
				onBookingCreated={vi.fn()}
				token="mock-token"
			/>,
		);

		expect(
			await screen.findByText("Instrutor não encontrado ou indisponível para agendamento."),
		).toBeInTheDocument();
		expect(getSlots).not.toHaveBeenCalled();

		await user.click(screen.getByRole("button", { name: "Voltar para a busca" }));
		expect(onBack).toHaveBeenCalled();
	});
});
