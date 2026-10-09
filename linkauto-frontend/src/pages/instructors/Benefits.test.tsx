import { screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import Benefits from "./Benefits";
import { renderWithProviders } from "../../test/renderWithProviders";

describe("Benefits Page", () => {
	it("renders main heading and benefit cards", () => {
		renderWithProviders(<Benefits />);

		expect(screen.getAllByText(/Ganhe até 3x mais/i).length).toBeGreaterThanOrEqual(1);
		expect(screen.getByText(/Autonomia Total/i)).toBeInTheDocument();
		expect(screen.getByText(/Pagamento Direto/i)).toBeInTheDocument();
		expect(screen.getByRole("link", { name: /Começar Agora/i })).toBeInTheDocument();
	});

	it("does not claim platform payments or unverifiable earnings (RN06)", () => {
		renderWithProviders(<Benefits />);

		expect(
			screen.queryByText(/Pagamentos Seguros/i),
		).not.toBeInTheDocument();
		expect(
			screen.queryByText(/Receba seus ganhos semanalmente via PIX/i),
		).not.toBeInTheDocument();
		expect(
			screen.queryByText(/Garantia de Pagamento/i),
		).not.toBeInTheDocument();
		expect(
			screen.queryByText(/R\$ 6\.000/i),
		).not.toBeInTheDocument();
		expect(
			screen.getByText(/mais visibilidade e recebem mais pedidos/i),
		).toBeInTheDocument();
	});
});
