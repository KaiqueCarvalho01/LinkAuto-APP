import { screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import LicensedDrivers from "./LicensedDrivers";
import { renderWithProviders } from "../../test/renderWithProviders";

describe("LicensedDrivers Page", () => {
	it("renders main heading and key sections", () => {
		renderWithProviders(<LicensedDrivers />);

		expect(screen.getByText(/Volte a Dirigir com Confiança/i)).toBeInTheDocument();
		expect(screen.getByText(/Perder o Medo/i)).toBeInTheDocument();
		expect(screen.getByText(/Por que escolher o LinkAuto\?/i)).toBeInTheDocument();
		expect(screen.getByRole("link", { name: /Encontrar Instrutor Especializado/i })).toBeInTheDocument();
	});
});
