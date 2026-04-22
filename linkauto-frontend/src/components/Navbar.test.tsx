import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";

import { Navbar } from "./Navbar";
import { renderWithProviders } from "../test/renderWithProviders";

describe("Navbar (Visitor State)", () => {
	it("renders main navigation links for visitors", () => {
		renderWithProviders(<Navbar />);

		expect(
			screen.getByRole("link", { name: /Explorar/i }),
		).toBeInTheDocument();
		expect(
			screen.getByRole("button", { name: /Para Alunos/i }),
		).toBeInTheDocument();
		expect(
			screen.getByRole("button", { name: /Para Instrutores/i }),
		).toBeInTheDocument();
		expect(
			screen.getByRole("link", { name: /Sobre/i }),
		).toBeInTheDocument();
		expect(
			screen.getByRole("link", { name: /Contato/i }),
		).toBeInTheDocument();
		expect(
			screen.getByRole("link", { name: /Entrar/i }),
		).toBeInTheDocument();
		expect(
			screen.getByRole("link", { name: /Comece agora/i }),
		).toBeInTheDocument();
	});

	it("opens 'Para Alunos' dropdown menu", async () => {
		const user = userEvent.setup();
		renderWithProviders(<Navbar />);

		const menuButton = screen.getByRole("button", { name: /Para Alunos/i });
		await user.click(menuButton);

		expect(
			screen.getByRole("link", { name: /Primeira Habilitação/i }),
		).toBeInTheDocument();
		expect(
			screen.getByRole("link", { name: /Habilitados/i }),
		).toBeInTheDocument();
		expect(
			screen.getByRole("link", { name: /Como Funciona/i }),
		).toBeInTheDocument();
		expect(
			screen.getByRole("link", { name: /Ver Instrutores/i }),
		).toBeInTheDocument();
	});

	it("opens 'Para Instrutores' dropdown menu", async () => {
		const user = userEvent.setup();
		renderWithProviders(<Navbar />);

		const menuButton = screen.getByRole("button", {
			name: /Para Instrutores/i,
		});
		await user.click(menuButton);

		expect(
			screen.getByRole("link", { name: /Cadastre-se/i }),
		).toBeInTheDocument();
		expect(
			screen.getByRole("link", { name: /Como Funciona/i }),
		).toBeInTheDocument();
		expect(
			screen.getByRole("link", { name: /Vantagens/i }),
		).toBeInTheDocument();
		expect(
			screen.getByRole("link", { name: /Simulador/i }),
		).toBeInTheDocument();
	});
});
