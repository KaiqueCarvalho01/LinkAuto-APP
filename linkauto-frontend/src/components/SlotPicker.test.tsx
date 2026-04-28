import { useState } from "react";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";

import { SlotPicker } from "./SlotPicker";
import { renderWithProviders } from "../test/renderWithProviders";
import type { BookingSlot } from "../types/booking";

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
		label: "10:00 - 11:00",
		startAt: "2026-05-22T10:00:00.000Z",
		endAt: "2026-05-22T11:00:00.000Z",
		state: "RESERVADO",
	},
];

function SlotPickerHarness() {
	const [selectedIds, setSelectedIds] = useState<string[]>([]);

	return (
		<SlotPicker
			slots={slots}
			selectedIds={selectedIds}
			onSelectedIdsChange={setSelectedIds}
		/>
	);
}

describe("SlotPicker", () => {
	it("shows warning with a single selected slot and success with two consecutive slots", async () => {
		const user = userEvent.setup();
		renderWithProviders(<SlotPickerHarness />);

		await user.click(screen.getByTestId("slot-slot-1"));
		expect(
			screen.getByText("A reserva exige no minimo 2 horas consecutivas."),
		).toBeInTheDocument();

		await user.click(screen.getByTestId("slot-slot-2"));
		expect(
			screen.getByText("Selecao valida para solicitar o agendamento."),
		).toBeInTheDocument();
	});

	it("keeps reserved slots disabled", () => {
		renderWithProviders(<SlotPickerHarness />);

		expect(screen.getByTestId("slot-slot-3")).toBeDisabled();
	});
});
