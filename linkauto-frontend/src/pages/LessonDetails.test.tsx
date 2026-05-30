import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import LessonDetails from "./LessonDetails";
import { mockInstructors, getMockSlotsByInstructor } from "../test/fixtures/mockData";
import { renderWithProviders } from "../test/renderWithProviders";
import { slotService } from "../services/slotService";
import { bookingService } from "../services/bookingService";

describe("LessonDetails", () => {
	it("enables booking request only after valid slot selection", async () => {
		const onBookingCreated = vi.fn();
		const onBack = vi.fn();
		const user = userEvent.setup();
		const primaryInstructor = mockInstructors[0];

		if (!primaryInstructor) {
			throw new Error("Missing mock instructor for test");
		}

		// Mock service layer calls to isolate UI behavior and ensure clean async tests
		vi.spyOn(slotService, "getInstructorSlots").mockResolvedValue(
			getMockSlotsByInstructor(primaryInstructor.id)
		);
		vi.spyOn(bookingService, "createBooking").mockResolvedValue({} as any);

		renderWithProviders(
			<LessonDetails
				instructor={primaryInstructor}
				onBack={onBack}
				onBookingCreated={onBookingCreated}
				token="mock-token"
			/>,
		);

		const submitButton = screen.getByRole("button", {
			name: "Solicitar agendamento",
		});
		expect(submitButton).toBeDisabled();

		// Use findByTestId to wait for async slots to finish fetching and render
		const slot0 = await screen.findByTestId("slot-instr-001-slot-0");
		await user.click(slot0);
		expect(submitButton).toBeDisabled();

		const slot1 = await screen.findByTestId("slot-instr-001-slot-1");
		await user.click(slot1);
		expect(submitButton).toBeEnabled();

		await user.click(submitButton);
		
		await vi.waitFor(() => {
			expect(onBookingCreated).toHaveBeenCalled();
		});
	});
});
