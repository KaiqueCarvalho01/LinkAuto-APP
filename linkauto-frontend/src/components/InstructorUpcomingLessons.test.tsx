import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { InstructorUpcomingLessons } from "./InstructorUpcomingLessons";
import { bookingService } from "../services/bookingService";
import { httpClient } from "../services/httpClient";
import { renderWithProviders } from "../test/renderWithProviders";

const LESSON = {
	id: "b1",
	name: "Ana Souza",
	city: "Praça central",
	date: "Segunda-feira, 05/01/2099",
	time: "09:00 - 11:00",
};

const apiBooking = (id: string, startsAt: string) => ({
	id,
	student_id: "s",
	instructor_id: "i",
	status: "CONFIRMADA",
	location_description: null,
	latitude: null,
	longitude: null,
	created_at: "2026-10-18T10:00:00Z",
	confirmed_at: null,
	cancelled_at: null,
	cancelled_by: null,
	cancellation_reason: null,
	slots: [{ id: `${id}-l`, booking_id: id, slot_id: `${id}-s`, slot: { starts_at: startsAt, ends_at: startsAt } }],
	student: { full_name: id, avatar_url: null },
});

describe("bookingService.getUpcomingLessons", () => {
	afterEach(() => {
		vi.restoreAllMocks();
	});

	it("returns the instructor's future confirmed lessons, soonest first", async () => {
		const getSpy = vi.spyOn(httpClient, "get").mockResolvedValue({
			data: [
				apiBooking("later", "2099-01-06T09:00:00Z"),
				apiBooking("past", "2000-01-01T09:00:00Z"),
				apiBooking("sooner", "2099-01-05T09:00:00Z"),
			],
			meta: {},
		} as never);

		const lessons = await bookingService.getUpcomingLessons("t");

		expect(getSpy).toHaveBeenCalledWith("/bookings?status=CONFIRMADA&as=instructor", {
			token: "t",
		});
		expect(lessons.map((lesson) => lesson.id)).toEqual(["sooner", "later"]);
	});
});

describe("InstructorUpcomingLessons", () => {
	afterEach(() => {
		vi.restoreAllMocks();
	});

	it("lists confirmed lessons and cancels one after confirmation", async () => {
		const user = userEvent.setup();
		const loadSpy = vi
			.spyOn(bookingService, "getUpcomingLessons")
			.mockResolvedValueOnce([LESSON])
			.mockResolvedValueOnce([]);
		const cancelSpy = vi.spyOn(bookingService, "cancelBooking").mockResolvedValue({} as never);
		renderWithProviders(<InstructorUpcomingLessons token="t" />);

		expect(await screen.findByText("Ana Souza")).toBeInTheDocument();
		expect(screen.getByText("09:00 - 11:00")).toBeInTheDocument();

		await user.click(screen.getByRole("button", { name: "Cancelar aula" }));
		await user.click(screen.getByRole("button", { name: "Sim, cancelar" }));

		await waitFor(() => {
			expect(cancelSpy).toHaveBeenCalledWith("b1", "t", "Cancelado pelo instrutor");
		});
		expect(await screen.findByText(/nenhuma aula confirmada/i)).toBeInTheDocument();
		expect(loadSpy).toHaveBeenCalledTimes(2);
	});

	it("keeps the lesson and explains when cancelling fails", async () => {
		const user = userEvent.setup();
		vi.spyOn(bookingService, "getUpcomingLessons").mockResolvedValue([LESSON]);
		vi.spyOn(bookingService, "cancelBooking").mockRejectedValue(new Error("boom"));
		renderWithProviders(<InstructorUpcomingLessons token="t" />);

		await user.click(await screen.findByRole("button", { name: "Cancelar aula" }));
		await user.click(screen.getByRole("button", { name: "Sim, cancelar" }));

		expect(await screen.findByRole("alert")).toHaveTextContent("Não foi possível cancelar");
		expect(screen.getByText("Ana Souza")).toBeInTheDocument();
	});
});
