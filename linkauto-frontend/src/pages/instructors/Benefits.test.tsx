import { screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import Benefits from "./Benefits";
import { renderWithProviders } from "../../test/renderWithProviders";

describe("Benefits Page", () => {
	it("renders main heading and benefit cards", () => {
		renderWithProviders(<Benefits />);

		expect(screen.getAllByText(/Ganhe até 3x mais/i).length).toBeGreaterThanOrEqual(1);
		expect(screen.getByText(/Autonomia Total/i)).toBeInTheDocument();
		expect(screen.getByText(/Pagamentos Seguros/i)).toBeInTheDocument();
		expect(screen.getByRole("link", { name: /Começar Agora/i })).toBeInTheDocument();
	});
});
