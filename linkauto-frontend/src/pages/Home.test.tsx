import { screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import Home from "./Home";
import { instructorService } from "../services/instructorService";
import { renderWithProviders } from "../test/renderWithProviders";

const renderHome = () =>
	renderWithProviders(
		<Home isAuthenticated={false} onOpenLogin={vi.fn()} onOpenSearch={vi.fn()} />,
	);

describe("Home instructor map", () => {
	beforeEach(() => {
		vi.restoreAllMocks();
	});

	it("never fills the map with made-up instructors when there are none", async () => {
		vi.spyOn(instructorService, "getPublicInstructors").mockResolvedValue([]);

		renderHome();

		expect(
			await screen.findByText("Ainda não há instrutores disponíveis no mapa."),
		).toBeInTheDocument();
		expect(screen.queryByText("Modo Demonstração")).not.toBeInTheDocument();
	});

	it("says the instructors couldn't be loaded when the request fails", async () => {
		vi.spyOn(instructorService, "getPublicInstructors").mockRejectedValue(
			new Error("Network down"),
		);

		renderHome();

		expect(
			await screen.findByText("Não foi possível carregar os instrutores."),
		).toBeInTheDocument();
		expect(screen.queryByText("Modo Demonstração")).not.toBeInTheDocument();
	});
});
