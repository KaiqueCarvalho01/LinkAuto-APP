import { screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import HowItWorks from "./HowItWorks";
import { renderWithProviders } from "../../test/renderWithProviders";

describe("HowItWorks Instructor Page", () => {
	it("renders main heading and instructor steps", () => {
		renderWithProviders(<HowItWorks />);

		expect(screen.getByText(/Seu novo escritório/i)).toBeInTheDocument();
		expect(screen.getByText(/1. Cadastro e Validação/i)).toBeInTheDocument();
		expect(screen.getByText(/2. Configure sua Agenda/i)).toBeInTheDocument();
		expect(screen.getByText(/Perguntas Frequentes/i)).toBeInTheDocument();
	});
});
