import { HttpClientError } from "../services/httpClient";

// An error as the API returns it: an error code and an English message
export const apiError = (status: number, code: string, message: string): HttpClientError =>
	new HttpClientError(message, status, { data: null, error: { code, message }, meta: {} });
