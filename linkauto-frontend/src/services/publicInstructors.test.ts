import { afterEach, describe, expect, it, vi } from "vitest";

import { mapApiBookingToPreview } from "./bookingService";
import { instructorService } from "./instructorService";
import type { ApiBookingResource } from "../types/api.types";

const jsonResponse = (body: unknown): Response =>
	new Response(JSON.stringify(body), {
		status: 200,
		headers: { "content-type": "application/json" },
	});

describe("instructorService.getPublicInstructors", () => {
	afterEach(() => {
		vi.unstubAllGlobals();
	});

	it("maps the public-safe payload and identifies instructors by slug", async () => {
		vi.stubGlobal(
			"fetch",
			vi.fn().mockResolvedValue(
				jsonResponse({
					data: [
						{
							id: "camila-rocha-mogi-mirim-8f2a",
							slug: "camila-rocha-mogi-mirim-8f2a",
							full_name: "Camila Rocha",
							avatar_url: null,
							city: "Mogi Mirim",
							state: "SP",
							bio: null,
							specialties: ["Carro"],
							price_per_hour: 70,
							rating_avg: 4.8,
							rating_count: 5,
							latitude: -22.43,
							longitude: -46.95,
							action_radius_km: 15,
						},
					],
					error: null,
					meta: { total: 1 },
				}),
			),
		);

		const [instructor] = await instructorService.getPublicInstructors();

		expect(instructor).toMatchObject({
			id: "camila-rocha-mogi-mirim-8f2a",
			slug: "camila-rocha-mogi-mirim-8f2a",
			fullName: "Camila Rocha",
			hourlyRate: 70,
			radiusKm: 15,
			coordinates: { lat: -22.43, lng: -46.95 },
		});
	});
});

describe("mapApiBookingToPreview", () => {
	const baseBooking: ApiBookingResource = {
		id: "booking-1",
		student_id: "student-uuid",
		instructor_id: "instructor-uuid",
		status: "PENDENTE",
		location_description: null,
		latitude: null,
		longitude: null,
		created_at: "2026-10-08T10:00:00Z",
		confirmed_at: null,
		cancelled_at: null,
		cancelled_by: null,
		cancellation_reason: null,
		slots: [],
		instructor: {
			slug: "rafael-mendes-mogi-guacu-3c1d",
			full_name: "Rafael Mendes",
			avatar_url: null,
			city: "Mogi Guaçu",
			state: "SP",
		},
	};

	it("uses the instructor's public summary embedded in the booking", () => {
		const preview = mapApiBookingToPreview(baseBooking);

		expect(preview.instructor.id).toBe("rafael-mendes-mogi-guacu-3c1d");
		expect(preview.instructor.slug).toBe("rafael-mendes-mogi-guacu-3c1d");
		expect(preview.instructor.fullName).toBe("Rafael Mendes");
		expect(preview.instructor.city).toBe("Mogi Guaçu");
	});

	it("falls back to a placeholder when the booking has no instructor summary", () => {
		const preview = mapApiBookingToPreview({ ...baseBooking, instructor: null });

		expect(preview.instructor.fullName).toBe("Instrutor LinkAuto");
	});
});
