import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";

import Simulator from "./Simulator";
import { renderWithProviders } from "../../test/renderWithProviders";

describe("Simulator Page", () => {
	it("renders simulator heading and interactive elements", () => {
		renderWithProviders(<Simulator />);

		expect(screen.getByText(/Potencial de Ganhos/i)).toBeInTheDocument();
		expect(screen.getByLabelText(/Valor da Hora/i)).toBeInTheDocument();
		expect(screen.getByLabelText(/Aulas por Semana/i)).toBeInTheDocument();
	});

	it("calculates earnings dynamically", async () => {
		const user = userEvent.setup();
		renderWithProviders(<Simulator />);

		const hourInput = screen.getByLabelText(/Valor da Hora/i);
		const weekInput = screen.getByLabelText(/Aulas por Semana/i);

		await user.clear(hourInput);
		await user.type(hourInput, "100");
		
		await user.clear(weekInput);
		await user.type(weekInput, "20");

		// 100 * 20 * 4 weeks = 8000
		expect(screen.getByText(/R\$ 8\.000/i)).toBeInTheDocument();
	});
});
