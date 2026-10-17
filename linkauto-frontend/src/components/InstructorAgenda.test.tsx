import { fireEvent, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { InstructorAgenda, buildSlotTimes } from "./InstructorAgenda";
import { HttpClientError } from "../services/httpClient";
import { slotService } from "../services/slotService";
import { renderWithProviders } from "../test/renderWithProviders";
import type { BookingSlot } from "../types/booking";

const slot = (id: string, startAt: string, endAt: string, state: BookingSlot["state"]) => ({
	id,
	label: `${startAt.slice(11, 16)} - ${endAt.slice(11, 16)}`,
	startAt,
	endAt,
	state,
});

const AGENDA: BookingSlot[] = [
	slot("past", "2000-01-03T09:00:00Z", "2000-01-03T10:00:00Z", "DISPONIVEL"),
	slot("free", "2099-01-05T09:00:00Z", "2099-01-05T10:00:00Z", "DISPONIVEL"),
	slot("taken", "2099-01-05T10:00:00Z", "2099-01-05T11:00:00Z", "RESERVADO"),
	slot("later", "2099-01-06T14:00:00Z", "2099-01-06T15:00:00Z", "DISPONIVEL"),
];

describe("InstructorAgenda", () => {
	afterEach(() => {
		vi.restoreAllMocks();
	});

	it("lists upcoming slots by day and only lets free ones be removed", async () => {
		vi.spyOn(slotService, "getMySlots").mockResolvedValue(AGENDA);

		renderWithProviders(<InstructorAgenda token="t" />);

		expect(await screen.findByText("Segunda-feira, 05/01/2099")).toBeInTheDocument();
		expect(screen.getByText("Terça-feira, 06/01/2099")).toBeInTheDocument();
		expect(screen.queryByText(/2000/)).not.toBeInTheDocument();
		expect(screen.getByText("Reservado")).toBeInTheDocument();
		// Two free upcoming slots can be removed; the reserved one can't
		expect(screen.getAllByRole("button", { name: /remover horário/i })).toHaveLength(2);
	});

	it("opens consecutive one-hour slots on the chosen day", async () => {
		const user = userEvent.setup();
		const getSpy = vi.spyOn(slotService, "getMySlots").mockResolvedValue([]);
		const createSpy = vi
			.spyOn(slotService, "createSlot")
			.mockResolvedValue(AGENDA[1] as BookingSlot);
		renderWithProviders(<InstructorAgenda token="t" />);

		fireEvent.change(screen.getByLabelText("Dia"), { target: { value: "2099-01-05" } });
		await user.selectOptions(screen.getByLabelText("Início"), "9");
		await user.selectOptions(screen.getByLabelText("Horas seguidas"), "2");
		await user.click(screen.getByRole("button", { name: /abrir horários/i }));

		await waitFor(() => {
			expect(createSpy).toHaveBeenCalledTimes(2);
		});
		expect(createSpy).toHaveBeenNthCalledWith(
			1,
			{ starts_at: "2099-01-05T09:00:00Z", ends_at: "2099-01-05T10:00:00Z" },
			"t",
		);
		expect(createSpy).toHaveBeenNthCalledWith(
			2,
			{ starts_at: "2099-01-05T10:00:00Z", ends_at: "2099-01-05T11:00:00Z" },
			"t",
		);
		await waitFor(() => {
			expect(getSpy).toHaveBeenCalledTimes(2);
		});
	});

	it("explains an overlap", async () => {
		const user = userEvent.setup();
		vi.spyOn(slotService, "getMySlots").mockResolvedValue([]);
		vi.spyOn(slotService, "createSlot").mockRejectedValue(
			new HttpClientError("overlap", 409, null),
		);
		renderWithProviders(<InstructorAgenda token="t" />);

		fireEvent.change(screen.getByLabelText("Dia"), { target: { value: "2099-01-05" } });
		await user.click(screen.getByRole("button", { name: /abrir horários/i }));

		expect(await screen.findByRole("alert")).toHaveTextContent(
			"Já existe um horário seu nesse período.",
		);
	});

	it("removes a free slot", async () => {
		const user = userEvent.setup();
		vi.spyOn(slotService, "getMySlots").mockResolvedValue(AGENDA);
		const deleteSpy = vi.spyOn(slotService, "deleteSlot").mockResolvedValue({ deleted: true });
		renderWithProviders(<InstructorAgenda token="t" />);

		const day = (await screen.findByText("Terça-feira, 06/01/2099")).parentElement as HTMLElement;
		await user.click(within(day).getByRole("button", { name: /remover horário/i }));

		await waitFor(() => {
			expect(deleteSpy).toHaveBeenCalledWith("later", "t");
		});
	});

	it("tells instructors awaiting approval that their slots aren't public yet", () => {
		vi.spyOn(slotService, "getMySlots").mockResolvedValue([]);

		renderWithProviders(<InstructorAgenda token="t" awaitingApproval />);

		expect(screen.getByText(/visíveis para os alunos depois/i)).toBeInTheDocument();
	});
});

describe("buildSlotTimes", () => {
	it("builds back-to-back one-hour slots on the UTC clock", () => {
		expect(buildSlotTimes("2099-01-05", 21, 1)).toEqual([
			{ starts_at: "2099-01-05T21:00:00Z", ends_at: "2099-01-05T22:00:00Z" },
		]);
	});
});
