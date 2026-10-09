import { screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import HowItWorks from "./HowItWorks";
import { renderWithProviders } from "../../test/renderWithProviders";

describe("HowItWorks Student Page", () => {
	it("renders main heading and steps", () => {
		renderWithProviders(<HowItWorks />);

		expect(screen.getByText(/O Caminho para a Autonomia/i)).toBeInTheDocument();
		expect(screen.getByText(/1. Busque/i)).toBeInTheDocument();
		expect(screen.getByText(/2. Agende/i)).toBeInTheDocument();
		expect(screen.getByText(/3. Dirija/i)).toBeInTheDocument();
		expect(screen.getByText(/Custos e Transparência/i)).toBeInTheDocument();
	});

	it("does not claim the platform processes payments (RN06)", () => {
		renderWithProviders(<HowItWorks />);

		expect(
			screen.queryByText(/pague com segurança via PIX/i),
		).not.toBeInTheDocument();
		expect(
			screen.queryByText(/dinheiro fica protegido/i),
		).not.toBeInTheDocument();
		expect(
			screen.queryByText(/reembolso total/i),
		).not.toBeInTheDocument();
	});
});
