import { screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { renderWithProviders } from "../test/renderWithProviders";
import Cadastro from "./Cadastro";
import Sobre from "./Sobre";
import Contato from "./Contato";
import Notificacoes from "./Notificacoes";
import Ajuda from "./Ajuda";
import AuditLog from "./admin/AuditLog";
import PrimeiraHabilitacao from "./alunos/PrimeiraHabilitacao";
import Habilitados from "./alunos/Habilitados";
import ComoFuncionaAluno from "./alunos/ComoFunciona";
import ComoFuncionaInstrutor from "./instrutores/ComoFunciona";
import Vantagens from "./instrutores/Vantagens";
import Simulador from "./instrutores/Simulador";

describe("Scaffold Pages", () => {
	it("renders Cadastro page", () => {
		renderWithProviders(<Cadastro />);
		expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("Cadastro");
	});

	it("renders Sobre page", () => {
		renderWithProviders(<Sobre />);
		expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("Sobre");
	});

	it("renders Contato page", () => {
		renderWithProviders(<Contato />);
		expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("Contato");
	});

	it("renders Notificacoes page", () => {
		renderWithProviders(<Notificacoes />);
		expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("Notificações");
	});

	it("renders Ajuda page", () => {
		renderWithProviders(<Ajuda />);
		expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("Ajuda");
	});

	it("renders AuditLog page", () => {
		renderWithProviders(<AuditLog />);
		expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("Audit Log");
	});

	it("renders PrimeiraHabilitacao page", () => {
		renderWithProviders(<PrimeiraHabilitacao />);
		expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("Primeira Habilitação");
	});

	it("renders Habilitados page", () => {
		renderWithProviders(<Habilitados />);
		expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("Habilitados");
	});

	it("renders alunos ComoFunciona page", () => {
		renderWithProviders(<ComoFuncionaAluno />);
		expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("Como Funciona para Alunos");
	});

	it("renders instrutores ComoFunciona page", () => {
		renderWithProviders(<ComoFuncionaInstrutor />);
		expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("Como Funciona para Instrutores");
	});

	it("renders Vantagens page", () => {
		renderWithProviders(<Vantagens />);
		expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("Vantagens");
	});

	it("renders Simulador page", () => {
		renderWithProviders(<Simulador />);
		expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("Simulador");
	});
});
