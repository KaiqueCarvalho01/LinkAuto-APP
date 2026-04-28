import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import Register from "./Register";
import { renderWithProviders } from "../test/renderWithProviders";

describe("Register", () => {
	it("renders registration form with required fields", () => {
		renderWithProviders(<Register onRegister={vi.fn()} />);

		expect(
			screen.getByRole("heading", {
				name: /Crie sua conta/i,
				hidden: true,
			}),
		).toBeInTheDocument();
		expect(screen.getByLabelText(/Nome Completo/i)).toBeInTheDocument();
		expect(screen.getByLabelText(/E-mail/i)).toBeInTheDocument();
		expect(
			screen.getAllByLabelText(/Senha/i).length,
		).toBeGreaterThanOrEqual(1);
		expect(screen.getByLabelText(/Confirmar Senha/i)).toBeInTheDocument();
		expect(
			screen.getByRole("button", { name: /Aluno/i, hidden: true }),
		).toBeInTheDocument();
		expect(
			screen.getByRole("button", { name: /Instrutor/i, hidden: true }),
		).toBeInTheDocument();
		expect(
			screen.getByRole("button", { name: /Criar Conta/i, hidden: true }),
		).toBeInTheDocument();
	});

	it("shows error when passwords do not match", async () => {
		const user = userEvent.setup();
		renderWithProviders(<Register onRegister={vi.fn()} />);

		await user.type(screen.getByLabelText(/Nome Completo/i), "João Silva");
		await user.type(screen.getByLabelText(/E-mail/i), "joao@example.com");

		const passwordFields = screen.getAllByLabelText(/Senha/i);
		const mainPasswordField = passwordFields[0];
		const confirmPasswordField = screen.getByLabelText(/Confirmar Senha/i);

		if (mainPasswordField) {
			await user.type(mainPasswordField, "SenhaForte123");
		}
		await user.type(confirmPasswordField, "SenhaErrada123");

		await user.click(
			screen.getByRole("button", { name: /Criar Conta/i, hidden: true }),
		);

		expect(
			screen.getByText(/As senhas não coincidem/i),
		).toBeInTheDocument();
	});

	it("submits registration payload with selected role", async () => {
		const user = userEvent.setup();
		const onRegisterMock = vi.fn().mockResolvedValue(undefined);
		renderWithProviders(<Register onRegister={onRegisterMock} />);

		// Select Instructor role
		await user.click(
			screen.getByRole("button", { name: "Instrutor", hidden: true }),
		);

		await user.type(screen.getByLabelText(/Nome Completo/i), "Maria Souza");
		await user.type(screen.getByLabelText(/E-mail/i), "maria@example.com");

		const passwordFields = screen.getAllByLabelText(/Senha/i);
		const mainPasswordField = passwordFields[0];
		if (mainPasswordField) {
			await user.type(mainPasswordField, "SenhaForte123");
		}
		await user.type(
			screen.getByLabelText(/Confirmar Senha/i),
			"SenhaForte123",
		);

		await user.click(
			screen.getByRole("button", { name: /Criar Conta/i, hidden: true }),
		);

		expect(onRegisterMock).toHaveBeenCalledWith({
			name: "Maria Souza",
			email: "maria@example.com",
			password: "SenhaForte123",
			preferredRole: "instructor",
		});
	});

	it("displays server error message on failure", async () => {
		const user = userEvent.setup();
		const errorMsg = "E-mail já está em uso.";
		const onRegisterMock = vi.fn().mockRejectedValue(new Error(errorMsg));
		renderWithProviders(<Register onRegister={onRegisterMock} />);

		await user.type(screen.getByLabelText(/Nome Completo/i), "João Silva");
		await user.type(screen.getByLabelText(/E-mail/i), "joao@example.com");

		const passwordFields = screen.getAllByLabelText(/Senha/i);
		const mainPasswordField = passwordFields[0];
		if (mainPasswordField) {
			await user.type(mainPasswordField, "SenhaForte123");
		}
		await user.type(
			screen.getByLabelText(/Confirmar Senha/i),
			"SenhaForte123",
		);

		await user.click(
			screen.getByRole("button", { name: /Criar Conta/i, hidden: true }),
		);

		expect(await screen.findByText(errorMsg)).toBeInTheDocument();
	});
});
