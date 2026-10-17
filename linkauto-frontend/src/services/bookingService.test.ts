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
