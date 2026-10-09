import { screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import FirstLicense from "./FirstLicense";
import { renderWithProviders } from "../../test/renderWithProviders";

describe("FirstLicense Page", () => {
	it("renders main heading and key sections", () => {
		renderWithProviders(<FirstLicense />);

		// Use more robust matching for broken up text
		expect(screen.getByRole("heading", { name: /Sua CNH com Liberdade/i })).toBeInTheDocument();
		expect(screen.getByText(/Por que escolher o LinkAuto\?/i)).toBeInTheDocument();
		expect(screen.getByText(/Segurança em Primeiro Lugar/i)).toBeInTheDocument();
		expect(screen.getByRole("link", { name: /Começar Agora/i })).toBeInTheDocument();
	});

	it("does not claim escrow payments (RN06)", () => {
		renderWithProviders(<FirstLicense />);

		expect(
			screen.queryByText(/Pagamento Seguro/i),
		).not.toBeInTheDocument();
		expect(
			screen.queryByText(/só é liberado para o instrutor/i),
		).not.toBeInTheDocument();
	});
});
