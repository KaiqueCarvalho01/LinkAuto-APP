import { HttpClientError } from "./httpClient";

// The API's error messages are in English and meant for developers: users see these
// instead, by error code. Screens can say what a code means in their context.
const MESSAGES: Record<string, string> = {
	UNAUTHORIZED: "Sua sessão expirou. Entre novamente.",
	FORBIDDEN: "Você não tem permissão para fazer isso.",
	NOT_FOUND: "Não encontramos o que você procurou. Pode ter sido removido.",
	VALIDATION_ERROR: "Alguns dados estão inválidos. Confira e tente novamente.",
	CONFLICT: "Os dados mudaram enquanto isso. Atualize a página e tente novamente.",
	INVALID_TRANSITION: "Esta ação não é mais possível. Atualize a página.",
	RATE_LIMIT_EXCEEDED:
		"Muitas tentativas em pouco tempo. Aguarde alguns minutos e tente novamente.",
	PAYLOAD_TOO_LARGE: "Os dados enviados são grandes demais.",
	INVALID_TOKEN: "Este link é inválido, já foi usado ou expirou. Solicite um novo link.",
	INSTRUCTOR_NOT_FOUND: "Instrutor não encontrado ou indisponível para agendamento.",
	STUDENT_PENALIZED:
		"Sua conta está penalizada e temporariamente impedida de agendar novas aulas.",
	SLOT_VALIDATION: "Os horários selecionados são inválidos ou não são consecutivos.",
	SLOT_OVERLAP: "Já existe um horário seu nesse período.",
};

const SERVER_UNAVAILABLE = "O servidor está indisponível no momento. Tente novamente em instantes.";
const CONNECTION_FAILED = "Não foi possível conectar ao servidor. Verifique sua conexão.";

export const apiErrorMessage = (
	err: unknown,
	fallback: string,
	overrides: Readonly<Record<string, string>> = {},
): string => {
	if (err instanceof HttpClientError) {
		const code = err.payload?.error.code;
		if (code) return overrides[code] ?? MESSAGES[code] ?? fallback;
		return err.status >= 500 ? SERVER_UNAVAILABLE : fallback;
	}
	// fetch rejects with a TypeError when the request never reaches the server
	if (err instanceof TypeError) return CONNECTION_FAILED;
	return fallback;
};
