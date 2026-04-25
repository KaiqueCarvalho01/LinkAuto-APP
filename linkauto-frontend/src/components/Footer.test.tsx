import { screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { Footer } from "./Footer";
import { renderWithProviders } from "../test/renderWithProviders";

describe("Footer", () => {
	it("should render the footer component", () => {
		renderWithProviders(<Footer />);
		expect(screen.getByRole("contentinfo")).toBeInTheDocument();
	});

	it("should display the copyright text", () => {
		renderWithProviders(<Footer />);
		expect(
			screen.getByText(
				/© 2026 LinkAuto\. Todos os direitos reservados\./i,
			),
		).toBeInTheDocument();
	});

	it("should have three columns of links in Portuguese", () => {
		renderWithProviders(<Footer />);
		expect(screen.getByText(/Alunos/i)).toBeInTheDocument();
		expect(screen.getByText(/Instrutores/i)).toBeInTheDocument();
		expect(screen.getByText(/Institucional/i)).toBeInTheDocument();
	});

	it("should have the correct links under the Alunos column", () => {
		renderWithProviders(<Footer />);
		expect(
			screen.getByRole("link", { name: /Primeira Habilitação/i }),
		).toHaveAttribute("href", "/students/first-license");
		expect(
			screen.getByRole("link", { name: /Buscar Instrutor/i }),
		).toHaveAttribute("href", "/search");
		expect(
			screen.getByRole("link", { name: /Minhas Aulas/i }),
		).toHaveAttribute("href", "/student/lessons");
	});

	it("should have the correct links under the Instrutores column", () => {
		renderWithProviders(<Footer />);
		expect(
			screen.getByRole("link", { name: /Cadastrar como Instrutor/i }),
		).toHaveAttribute("href", "/instructors/register");
		expect(
			screen.getByRole("link", { name: /Painel do Instrutor/i }),
		).toHaveAttribute("href", "/instructor/students");
		expect(
			screen.getByRole("link", { name: /Meus Veículos/i }),
		).toHaveAttribute("href", "/instructor/vehicles");
	});

	it("should have the correct links under the Institucional column", () => {
		renderWithProviders(<Footer />);
		expect(
			screen.getByRole("link", { name: /Sobre Nós/i }),
		).toHaveAttribute("href", "/about");
		expect(screen.getByRole("link", { name: /Contato/i })).toHaveAttribute(
			"href",
			"/contact",
		);
		expect(
			screen.getByRole("link", { name: /Termos de Uso/i }),
		).toHaveAttribute("href", "/terms");
	});
});
