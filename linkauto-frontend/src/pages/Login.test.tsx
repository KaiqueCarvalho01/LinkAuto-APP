import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import Login from "./Login";
import { renderWithProviders } from "../test/renderWithProviders";

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
});
