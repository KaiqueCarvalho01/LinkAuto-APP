import { describe, expect, it } from "vitest";

import {
	areSlotsConsecutive,
	bookingSelectionIsValid,
	getSelectedSlots,
} from "./bookingRules";
import type { BookingSlot } from "../../types/booking";

const slots: BookingSlot[] = [
	{
		id: "slot-1",
		label: "08:00 - 09:00",
		startAt: "2026-05-22T08:00:00.000Z",
		endAt: "2026-05-22T09:00:00.000Z",
		state: "DISPONIVEL",
	},
	{
		id: "slot-2",
		label: "09:00 - 10:00",
		startAt: "2026-05-22T09:00:00.000Z",
		endAt: "2026-05-22T10:00:00.000Z",
		state: "DISPONIVEL",
	},
	{
		id: "slot-3",
		label: "11:00 - 12:00",
		startAt: "2026-05-22T11:00:00.000Z",
		endAt: "2026-05-22T12:00:00.000Z",
		state: "DISPONIVEL",
	},
];

describe("bookingRules", () => {
	it("returns selected slots sorted by start time", () => {
		const selected = getSelectedSlots(slots, ["slot-2", "slot-1"]);

		expect(selected.map((item) => item.id)).toEqual(["slot-1", "slot-2"]);
	});

	it("accepts valid consecutive two-hour selection", () => {
		expect(bookingSelectionIsValid(slots, ["slot-1", "slot-2"])).toBe(true);
	});

	it("rejects selections with gaps", () => {
		expect(bookingSelectionIsValid(slots, ["slot-1", "slot-3"])).toBe(
			false,
		);
	});

	it("rejects selections with fewer than two slots", () => {
		expect(bookingSelectionIsValid(slots, ["slot-1"])).toBe(false);
	});

	it("rejects cross-day selections", () => {
		const crossDay: BookingSlot[] = [
			{
				id: "slot-a",
				label: "23:00 - 00:00",
				startAt: "2026-05-22T23:00:00.000Z",
				endAt: "2026-05-23T00:00:00.000Z",
				state: "DISPONIVEL",
			},
			{
				id: "slot-b",
				label: "00:00 - 01:00",
				startAt: "2026-05-23T00:00:00.000Z",
				endAt: "2026-05-23T01:00:00.000Z",
				state: "DISPONIVEL",
			},
		];

		expect(areSlotsConsecutive(crossDay)).toBe(false);
	});
});
