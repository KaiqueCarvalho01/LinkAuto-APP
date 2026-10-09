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

	it("does not claim the platform processes payments (RN06)", () => {
		renderWithProviders(<HowItWorks />);

		expect(
			screen.getByText(/combinhe o pagamento/i),
		).toBeInTheDocument();
		expect(
			screen.getByText(/diretamente entre você e o aluno/i),
		).toBeInTheDocument();
		expect(
			screen.queryByText(/pagamentos são processados pela plataforma/i),
		).not.toBeInTheDocument();
		expect(
			screen.queryByText(/conta LinkAuto/i),
		).not.toBeInTheDocument();
	});
});
