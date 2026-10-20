/* eslint-disable @typescript-eslint/no-explicit-any */
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import PasswordReset from "./PasswordReset";
import { renderWithProviders } from "../test/renderWithProviders";
import { httpClient } from "../services/httpClient";
import { apiError } from "../test/apiError";

describe("PasswordReset Page", () => {
	it("renders password reset form correctly", () => {
		renderWithProviders(<PasswordReset />);

		expect(screen.getByText(/Esqueceu a senha\?/i)).toBeInTheDocument();
		expect(screen.getByPlaceholderText("seu.email@exemplo.com")).toBeInTheDocument();
		expect(screen.getByRole("button", { name: /enviar link/i })).toBeInTheDocument();
	});

	it("submits email request successfully and displays success message", async () => {
		const user = userEvent.setup();
		const postSpy = vi.spyOn(httpClient, "post").mockResolvedValue({} as any);

		renderWithProviders(<PasswordReset />);

		const emailInput = screen.getByPlaceholderText("seu.email@exemplo.com");
		const submitBtn = screen.getByRole("button", { name: /enviar link/i });

		await user.type(emailInput, "test@exemplo.com");
		await user.click(submitBtn);

		await waitFor(() => {
			expect(postSpy).toHaveBeenCalledWith("/auth/password-reset", { email: "test@exemplo.com" });
		});

		expect(await screen.findByText(/Se o email estiver cadastrado, você receberá instruções/i)).toBeInTheDocument();
		expect(emailInput).not.toBeInTheDocument();
	});

	it("displays server error message on failure", async () => {
		const user = userEvent.setup();
		vi.spyOn(httpClient, "post").mockRejectedValue(
			apiError(429, "RATE_LIMIT_EXCEEDED", "Too many requests. Please try again later."),
		);

		renderWithProviders(<PasswordReset />);

		const emailInput = screen.getByPlaceholderText("seu.email@exemplo.com");
		const submitBtn = screen.getByRole("button", { name: /enviar link/i });

		await user.type(emailInput, "test@exemplo.com");
		await user.click(submitBtn);

		expect(
			await screen.findByText(
				"Muitas tentativas em pouco tempo. Aguarde alguns minutos e tente novamente.",
			),
		).toBeInTheDocument();
		expect(emailInput).toBeInTheDocument();
	});
});
