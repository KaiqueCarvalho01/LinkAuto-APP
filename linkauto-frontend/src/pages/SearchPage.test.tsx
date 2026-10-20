import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import SearchPage from "./SearchPage";
import { instructorService } from "../services/instructorService";
import { mockInstructors } from "../test/fixtures/mockData";
import { renderWithProviders } from "../test/renderWithProviders";

const renderSearch = () =>
	renderWithProviders(
		<SearchPage token="token" onOpenProfile={vi.fn()} onStartBooking={vi.fn()} />,
	);

describe("SearchPage", () => {
	beforeEach(() => {
		vi.restoreAllMocks();
	});

	it("tells a failed search apart from an empty result and lets the user retry", async () => {
		const user = userEvent.setup();
		const search = vi
			.spyOn(instructorService, "searchInstructors")
			.mockRejectedValueOnce(new Error("Network down"))
			.mockResolvedValueOnce(mockInstructors.slice(0, 1));

		renderSearch();

		expect(
			await screen.findByText("Não foi possível buscar instrutores."),
		).toBeInTheDocument();
		expect(screen.queryByText(/Nenhum instrutor encontrado/)).not.toBeInTheDocument();

		await user.click(screen.getByRole("button", { name: "Tentar novamente" }));

		expect(
			(await screen.findAllByText(mockInstructors[0]?.fullName ?? "")).length,
		).toBeGreaterThan(0);
		expect(screen.queryByText("Não foi possível buscar instrutores.")).not.toBeInTheDocument();
		expect(search).toHaveBeenCalledTimes(2);
	});

	it("labels every filter", () => {
		vi.spyOn(instructorService, "searchInstructors").mockResolvedValue([]);

		renderSearch();

		for (const name of ["Cidade", "Especialidade", "Raio de Busca (km)", "Ordenar por"]) {
			expect(screen.getByRole("combobox", { name })).toBeInTheDocument();
		}
		expect(screen.getByRole("spinbutton", { name: "Preço máximo (R$/h)" })).toBeInTheDocument();
	});

	it("suggests widening the filters when nothing matches", async () => {
		vi.spyOn(instructorService, "searchInstructors").mockResolvedValue([]);

		renderSearch();

		expect(
			await screen.findByText("Nenhum instrutor encontrado com este filtro."),
		).toBeInTheDocument();
		expect(screen.queryByText("Não foi possível buscar instrutores.")).not.toBeInTheDocument();
	});
});
