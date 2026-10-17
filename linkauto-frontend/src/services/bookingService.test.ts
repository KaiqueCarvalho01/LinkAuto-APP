import { afterEach, describe, expect, it, vi } from "vitest";

import { bookingService } from "./bookingService";
import { httpClient } from "./httpClient";

describe("bookingService.getMyBookings", () => {
	afterEach(() => {
		vi.restoreAllMocks();
	});

	it.each([
		[{}, "/bookings"],
		[{ as: "student" as const }, "/bookings?as=student"],
		[{ status: "PENDENTE", as: "instructor" as const }, "/bookings?status=PENDENTE&as=instructor"],
	])("builds the query for %o", async (options, expectedPath) => {
		const getSpy = vi
			.spyOn(httpClient, "get")
			.mockResolvedValue({ data: [], meta: {} } as never);

		await bookingService.getMyBookings("token", options);

		expect(getSpy).toHaveBeenCalledWith(expectedPath, { token: "token" });
	});
});

describe("bookingService.getPendingRequests", () => {
	afterEach(() => {
		vi.restoreAllMocks();
	});

	it("loads the instructor's pending bookings and names the student", async () => {
		const getSpy = vi.spyOn(httpClient, "get").mockResolvedValue({
			data: [
				{
					id: "b1",
					student_id: "s1",
					instructor_id: "i1",
					status: "PENDENTE",
					location_description: "Praça central",
					latitude: null,
					longitude: null,
					created_at: "2026-10-17T10:00:00Z",
					confirmed_at: null,
					cancelled_at: null,
					cancelled_by: null,
					cancellation_reason: null,
					slots: [
						{
							id: "bs1",
							booking_id: "b1",
							slot_id: "sl1",
							slot: { starts_at: "2026-10-18T09:00:00Z", ends_at: "2026-10-18T10:00:00Z" },
						},
						{
							id: "bs2",
							booking_id: "b1",
							slot_id: "sl2",
							slot: { starts_at: "2026-10-18T10:00:00Z", ends_at: "2026-10-18T11:00:00Z" },
						},
					],
					student: { full_name: "Ana Souza", avatar_url: null },
				},
			],
			meta: {},
		} as never);

		const requests = await bookingService.getPendingRequests("token");

		expect(getSpy).toHaveBeenCalledWith("/bookings?status=PENDENTE&as=instructor", {
			token: "token",
		});
		expect(requests).toEqual([
			{
				id: "b1",
				name: "Ana Souza",
				city: "Praça central",
				date: "Domingo, 18/10/2026",
				time: "09:00 - 11:00",
			},
		]);
	});
});
