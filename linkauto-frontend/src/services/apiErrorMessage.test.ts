import { describe, expect, it } from "vitest";

import { apiErrorMessage } from "./apiErrorMessage";
import { HttpClientError } from "./httpClient";
import { apiError as makeApiError } from "../test/apiError";

const apiError = (status: number, code: string, message = "Request validation failed.") =>
	makeApiError(status, code, message);

const FALLBACK = "Não foi possível concluir. Tente novamente.";

describe("apiErrorMessage", () => {
	it.each([
		[401, "UNAUTHORIZED", "Sua sessão expirou. Entre novamente."],
		[403, "FORBIDDEN", "Você não tem permissão para fazer isso."],
		[422, "VALIDATION_ERROR", "Alguns dados estão inválidos. Confira e tente novamente."],
		[
			429,
			"RATE_LIMIT_EXCEEDED",
			"Muitas tentativas em pouco tempo. Aguarde alguns minutos e tente novamente.",
		],
		[
			409,
			"CONFLICT",
			"Os dados mudaram enquanto isso. Atualize a página e tente novamente.",
		],
	])("translates %i %s", (status, code, expected) => {
		expect(apiErrorMessage(apiError(status, code), FALLBACK)).toBe(expected);
	});

	it("never shows the backend's English message", () => {
		const message = apiErrorMessage(
			apiError(400, "SOMETHING_NEW", "Email already registered"),
			FALLBACK,
		);

		expect(message).toBe(FALLBACK);
	});

	it("lets a screen say what a code means in its context", () => {
		expect(
			apiErrorMessage(apiError(401, "UNAUTHORIZED", "Invalid credentials."), FALLBACK, {
				UNAUTHORIZED: "E-mail ou senha incorretos.",
			}),
		).toBe("E-mail ou senha incorretos.");
	});

	it("explains server outages and connection failures", () => {
		expect(apiErrorMessage(new HttpClientError("HTTP 502", 502, null), FALLBACK)).toBe(
			"O servidor está indisponível no momento. Tente novamente em instantes.",
		);
		expect(apiErrorMessage(new TypeError("Failed to fetch"), FALLBACK)).toBe(
			"Não foi possível conectar ao servidor. Verifique sua conexão.",
		);
	});

	it("falls back for anything else", () => {
		expect(apiErrorMessage(new Error("boom"), FALLBACK)).toBe(FALLBACK);
		expect(apiErrorMessage("boom", FALLBACK)).toBe(FALLBACK);
	});
});
