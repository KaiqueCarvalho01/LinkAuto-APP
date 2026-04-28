import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";

import { FAQ } from "./FAQ";
import { renderWithProviders } from "../../test/renderWithProviders";

describe("FAQ", () => {
	it("renders FAQ title and common questions", () => {
		renderWithProviders(<FAQ />);

		expect(screen.getByText(/Perguntas Frequentes/i)).toBeInTheDocument();
		expect(screen.getByText(/Como pago as aulas?/i)).toBeInTheDocument();
		expect(screen.getByText(/Posso cancelar um agendamento?/i)).toBeInTheDocument();
	});

	it("expands an accordion item when clicked", async () => {
		const user = userEvent.setup();
		renderWithProviders(<FAQ />);

		const question = screen.getByText(/Como pago as aulas?/i);
		await user.click(question);

		// Check if answer is visible (simplified check for Chakra v3 Accordion)
		expect(screen.getByText(/Cartão de crédito ou PIX/i)).toBeInTheDocument();
	});
});
