import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ChakraProvider } from "@chakra-ui/react";
import { MemoryRouter, useLocation } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";

import PasswordResetConfirm from "./PasswordResetConfirm";
import { httpClient } from "../services/httpClient";
import { appSystem } from "../theme/system";

function CurrentUrl() {
	const location = useLocation();
	return <output data-testid="url">{location.pathname + location.search}</output>;
}

const renderAt = (path: string) =>
	render(
		<MemoryRouter initialEntries={[path]}>
			<ChakraProvider value={appSystem}>
				<PasswordResetConfirm />
				<CurrentUrl />
			</ChakraProvider>
		</MemoryRouter>,
	);

const fillPasswords = async (password: string, confirmation = password) => {
	const user = userEvent.setup();
	await user.type(screen.getByLabelText("Nova senha"), password);
	await user.type(screen.getByLabelText("Confirme a nova senha"), confirmation);
	await user.click(screen.getByRole("button", { name: /salvar nova senha/i }));
};

describe("PasswordResetConfirm", () => {
	afterEach(() => {
		vi.restoreAllMocks();
	});

	it("sends the token and the new password, then links to login", async () => {
		const postSpy = vi.spyOn(httpClient, "post").mockResolvedValue({} as never);
		renderAt("/password-reset/confirm?token=abc123");

		await fillPasswords("NovaSenha123");

		await waitFor(() => {
			expect(postSpy).toHaveBeenCalledWith("/auth/password-reset/confirm", {
				token: "abc123",
				new_password: "NovaSenha123",
			});
		});
		expect(await screen.findByText(/senha alterada com sucesso/i)).toBeInTheDocument();
		expect(screen.getByText("Fazer login")).toBeInTheDocument();
	});

	it("removes the token from the address bar", async () => {
		renderAt("/password-reset/confirm?token=abc123");

		await waitFor(() => {
			expect(screen.getByTestId("url")).toHaveTextContent(/^\/password-reset\/confirm$/);
		});
		expect(screen.getByRole("button", { name: /salvar nova senha/i })).toBeInTheDocument();
	});

	it("does not submit when the passwords differ", async () => {
		const postSpy = vi.spyOn(httpClient, "post");
		renderAt("/password-reset/confirm?token=abc123");

		await fillPasswords("NovaSenha123", "OutraSenha123");

		expect(await screen.findByText(/as senhas não coincidem/i)).toBeInTheDocument();
		expect(postSpy).not.toHaveBeenCalled();
	});

	it("shows an error for an invalid or expired link", async () => {
		vi.spyOn(httpClient, "post").mockRejectedValue(new Error("INVALID_TOKEN"));
		renderAt("/password-reset/confirm?token=expired");

		await fillPasswords("NovaSenha123");

		expect(await screen.findByText(/inválido, já foi usado ou expirou/i)).toBeInTheDocument();
	});

	it("asks for a new link when the token is missing", () => {
		renderAt("/password-reset/confirm");

		expect(screen.getByText(/link de redefinição inválido/i)).toBeInTheDocument();
		expect(screen.queryByRole("button", { name: /salvar nova senha/i })).not.toBeInTheDocument();
		expect(screen.getByText("Solicitar um novo link")).toBeInTheDocument();
	});
});
