import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import LessonDetails from "./LessonDetails";
import { mockInstructors } from "../services/mockData";
import { renderWithProviders } from "../test/renderWithProviders";

describe("LessonDetails", () => {
	it("enables booking request only after valid slot selection", async () => {
		const onBookingCreated = vi.fn();
		const onBack = vi.fn();
		const user = userEvent.setup();
		const primaryInstructor = mockInstructors[0];

		if (!primaryInstructor) {
			throw new Error("Missing mock instructor for test");
		}

		renderWithProviders(
			<LessonDetails
				instructor={primaryInstructor}
				onBack={onBack}
				onBookingCreated={onBookingCreated}
			/>,
		);

		const submitButton = screen.getByRole("button", {
			name: "Solicitar agendamento",
		});
		expect(submitButton).toBeDisabled();

		await user.click(screen.getByTestId("slot-instr-001-slot-0"));
		expect(submitButton).toBeDisabled();

		await user.click(screen.getByTestId("slot-instr-001-slot-1"));
		expect(submitButton).toBeEnabled();

		await user.click(submitButton);
		expect(onBookingCreated).toHaveBeenCalledWith({
			instructorId: "instr-001",
			slotIds: ["instr-001-slot-0", "instr-001-slot-1"],
		});
	});
});
