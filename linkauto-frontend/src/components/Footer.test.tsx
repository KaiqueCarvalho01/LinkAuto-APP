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
		expect(screen.getByText("Alunos")).toBeInTheDocument();
		expect(screen.getByText("Instrutores")).toBeInTheDocument();
		expect(screen.getByText("Institucional")).toBeInTheDocument();
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
		).toHaveAttribute("href", "/my-lessons");
	});

	it("should have the correct links under the Instrutores column", () => {
		renderWithProviders(<Footer />);
		expect(
			screen.getByRole("link", { name: /Cadastrar como Instrutor/i }),
		).toHaveAttribute("href", "/register?role=instructor");
		expect(
			screen.getByRole("link", { name: /Painel do Instrutor/i }),
		).toHaveAttribute("href", "/instructor/dashboard");
		// There is no vehicles page; the link only reopened the profile
		expect(
			screen.queryByRole("link", { name: /Meus Veículos/i }),
		).not.toBeInTheDocument();
	});

	it("has no placeholder links", () => {
		renderWithProviders(<Footer />);
		for (const link of screen.getAllByRole("link")) {
			expect(link.getAttribute("href")).not.toMatch(/^#?$/);
		}
		expect(
			screen.getByRole("link", { name: "E-mail de contato" }),
		).toHaveAttribute("href", "mailto:contato@linkauto.com.br");
	});

	it("should have the correct links under the Institucional column", () => {
		renderWithProviders(<Footer />);
		expect(
			screen.getByRole("link", { name: /Sobre Nós/i }),
		).toHaveAttribute("href", "/about");
		// Use getAllByRole because "Contato" also appears in aria-label of social link
		expect(screen.getAllByRole("link", { name: /Contato/i })[0]).toBeInTheDocument();
		expect(
			screen.getByRole("link", { name: /Termos de Uso/i }),
		).toHaveAttribute("href", "/terms");
	});

	it("should link Privacidade to the LGPD page and have no dead 'Em breve' links", () => {
		renderWithProviders(<Footer />);
		expect(
			screen.getByRole("link", { name: /Privacidade/i }),
		).toHaveAttribute("href", "/privacy");
		expect(
			screen.queryByRole("link", { name: /Cookies/i }),
		).not.toBeInTheDocument();
	});
});
