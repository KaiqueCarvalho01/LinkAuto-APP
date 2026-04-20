import type { BookingSlot } from "../../types/booking";

const asDate = (value: string): Date => new Date(value);

const sameUtcDay = (left: Date, right: Date): boolean => {
	return (
		left.getUTCFullYear() === right.getUTCFullYear() &&
		left.getUTCMonth() === right.getUTCMonth() &&
		left.getUTCDate() === right.getUTCDate()
	);
};

export const getSelectedSlots = (
	slots: BookingSlot[],
	selectedIds: string[],
): BookingSlot[] => {
	const selectedSet = new Set(selectedIds);
	return slots
		.filter((slot) => selectedSet.has(slot.id))
		.sort(
			(a, b) => asDate(a.startAt).getTime() - asDate(b.startAt).getTime(),
		);
};

export const areSlotsConsecutive = (slots: BookingSlot[]): boolean => {
	if (slots.length < 2) {
		return false;
	}

	const firstSlot = slots[0];
	if (!firstSlot) {
		return false;
	}
	const firstStart = asDate(firstSlot.startAt);

	for (let index = 1; index < slots.length; index += 1) {
		const previous = slots[index - 1];
		const current = slots[index];
		if (!previous || !current) {
			return false;
		}

		const previousEnd = asDate(previous.endAt);
		const currentStart = asDate(current.startAt);
		if (!sameUtcDay(firstStart, currentStart)) {
			return false;
		}

		if (!sameUtcDay(previousEnd, currentStart)) {
			return false;
		}

		const differenceMinutes =
			(currentStart.getTime() - previousEnd.getTime()) / (1000 * 60);
		if (differenceMinutes !== 0) {
			return false;
		}
	}

	return true;
};

export const bookingSelectionIsValid = (
	slots: BookingSlot[],
	selectedIds: string[],
): boolean => {
	if (selectedIds.length < 2) {
		return false;
	}

	const selectedSlots = getSelectedSlots(slots, selectedIds);
	return areSlotsConsecutive(selectedSlots);
};
