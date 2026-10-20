import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import Login from "./Login";
import { renderWithProviders } from "../test/renderWithProviders";
import { apiError } from "../test/apiError";

describe("Login", () => {
	it("submits authentication payload with selected role", async () => {
		const onAuthenticate = vi.fn().mockResolvedValue(undefined);
		const user = userEvent.setup();

		renderWithProviders(<Login onAuthenticate={onAuthenticate} />);

		await user.click(screen.getByRole("button", { name: "Instrutor" }));
		await user.type(screen.getByLabelText("E-mail"), "camila@linkauto.app");
		await user.type(screen.getByLabelText("Senha"), "SenhaForte123");
		await user.click(
			screen.getByRole("button", { name: "Entrar no LinkAuto" }),
		);

		expect(onAuthenticate).toHaveBeenCalledTimes(1);
		expect(onAuthenticate).toHaveBeenCalledWith({
			email: "camila@linkauto.app",
			password: "SenhaForte123",
			preferredRole: "instructor",
		});
	});

	it.each([
		[401, "UNAUTHORIZED", "Invalid credentials.", "E-mail ou senha incorretos."],
		[
			429,
			"RATE_LIMIT_EXCEEDED",
			"Too many requests. Please try again later.",
			"Muitas tentativas em pouco tempo. Aguarde alguns minutos e tente novamente.",
		],
	])("shows %i %s in Portuguese", async (status, code, english, portuguese) => {
		const user = userEvent.setup();
		renderWithProviders(
			<Login onAuthenticate={vi.fn().mockRejectedValue(apiError(status, code, english))} />,
		);

		await user.type(screen.getByLabelText("E-mail"), "camila@linkauto.app");
		await user.type(screen.getByLabelText("Senha"), "SenhaErrada1");
		await user.click(screen.getByRole("button", { name: "Entrar no LinkAuto" }));

		expect(await screen.findByText(portuguese)).toBeInTheDocument();
		expect(screen.queryByText(english)).not.toBeInTheDocument();
	});

	it("links 'Esqueceu a senha?' to password recovery and has no dead controls", () => {
		renderWithProviders(<Login onAuthenticate={vi.fn()} />);

		expect(screen.getByRole("link", { name: "Esqueceu a senha?" })).toHaveAttribute(
			"href",
			"/password-reset",
		);
		// "Manter conectado" did nothing: the session is always kept
		expect(screen.queryByText("Manter conectado")).not.toBeInTheDocument();
	});
});
