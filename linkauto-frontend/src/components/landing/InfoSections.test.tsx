import { screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { InfoSections } from "./InfoSections";
import { renderWithProviders } from "../../test/renderWithProviders";

describe("InfoSections", () => {
	it("renders 'Como Funciona' section with steps", () => {
		renderWithProviders(<InfoSections />);

		expect(screen.getByText(/Como Funciona/i)).toBeInTheDocument();
		expect(screen.getByText(/Busque por Proximidade/i)).toBeInTheDocument();
		expect(screen.getByText(/Agende sua Aula/i)).toBeInTheDocument();
		expect(screen.getByText(/Aprenda e Evolua/i)).toBeInTheDocument();
	});

	it("renders 'Para Alunos' and 'Para Instrutores' blocks", () => {
		renderWithProviders(<InfoSections />);

		expect(screen.getByText(/Para Alunos/i)).toBeInTheDocument();
		expect(screen.getByText(/Para Instrutores/i)).toBeInTheDocument();
	});

	it("renders 'Estatísticas' section", () => {
		renderWithProviders(<InfoSections />);

		expect(screen.getByText(/Nossos Números/i)).toBeInTheDocument();
		expect(screen.getByText(/Instrutores Ativos/i)).toBeInTheDocument();
		expect(screen.getByText(/Aulas Realizadas/i)).toBeInTheDocument();
	});
});
