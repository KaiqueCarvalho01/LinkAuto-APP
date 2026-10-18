import type { ApiErrorEnvelope, ApiSuccessEnvelope } from "../types/api";
import { API_BASE_URL } from "./config";

type HttpMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";

interface RequestOptions {
	body?: unknown;
	headers?: Record<string, string>;
	token?: string;
	signal?: AbortSignal;
}

export class HttpClientError extends Error {
	readonly status: number;
	readonly payload: ApiErrorEnvelope | null;

	constructor(
		message: string,
		status: number,
		payload: ApiErrorEnvelope | null,
	) {
		super(message);
		this.name = "HttpClientError";
		this.status = status;
		this.payload = payload;
	}
}

type TokenRefreshedCallback = (newAccessToken: string) => void;
type AuthFailureCallback = () => void;

let tokenRefreshedCallback: TokenRefreshedCallback | null = null;
let authFailureCallback: AuthFailureCallback | null = null;

export const setOnTokenRefreshed = (cb: TokenRefreshedCallback) => {
	tokenRefreshedCallback = cb;
};

export const setOnAuthFailure = (cb: AuthFailureCallback) => {
	authFailureCallback = cb;
};

const buildUrl = (path: string): string => {
	const normalizedPath = path.startsWith("/") ? path : `/${path}`;
	return `${API_BASE_URL}${normalizedPath}`;
};

const parseResponse = async (response: Response): Promise<unknown> => {
	const contentType = response.headers.get("content-type") || "";
	if (!contentType.includes("application/json")) {
		return null;
	}

	return response.json();
};

const isApiErrorEnvelope = (value: unknown): value is ApiErrorEnvelope => {
	if (typeof value !== "object" || value === null) {
		return false;
	}

	const maybeEnvelope = value as Partial<ApiErrorEnvelope>;
	return Boolean(
		maybeEnvelope.error && typeof maybeEnvelope.error.message === "string",
	);
};

const toHttpClientError = (status: number, payload: unknown): HttpClientError => {
	const typedPayload = isApiErrorEnvelope(payload) ? payload : null;
	const message = typedPayload?.error.message || `HTTP ${status}`;
	return new HttpClientError(message, status, typedPayload);
};

const toSuccessEnvelope = <TData>(payload: unknown): ApiSuccessEnvelope<TData> => {
	if (payload === null) {
		return { data: null as TData, error: null, meta: {} };
	}
	return payload as ApiSuccessEnvelope<TData>;
};

const request = async <TData>(
	method: HttpMethod,
	path: string,
	options: RequestOptions = {},
): Promise<ApiSuccessEnvelope<TData>> => {
	const { body, headers = {}, token, signal } = options;
	const isFormData = body instanceof FormData;
	let requestBody: BodyInit | undefined;
	if (body === undefined) {
		requestBody = undefined;
	} else if (isFormData) {
		requestBody = body;
	} else {
		requestBody = JSON.stringify(body);
	}

	const requestInit: RequestInit = {
		method,
		credentials: "include",
		headers: {
			...(isFormData ? {} : { "Content-Type": "application/json" }),
			...(token ? { Authorization: `Bearer ${token}` } : {}),
			...headers,
		},
	};

	if (signal) {
		requestInit.signal = signal;
	}

	if (requestBody !== undefined) {
		requestInit.body = requestBody;
	}

	const response = await fetch(buildUrl(path), requestInit);

	const payload = await parseResponse(response);
	if (!response.ok) {
		const isAuthEndpoint =
			path.includes("/auth/refresh") ||
			path.includes("/auth/login") ||
			path.includes("/auth/logout");
		if (response.status === 401 && !isAuthEndpoint) {
			const newAccessToken = await refreshAccessToken();
			const nextInit = {
				...requestInit,
				headers: { ...requestInit.headers, Authorization: `Bearer ${newAccessToken}` },
			};
			// Network errors on the retry propagate as-is: they don't end the session
			const nextResponse = await fetch(buildUrl(path), nextInit);
			const nextPayload = await parseResponse(nextResponse);
			if (!nextResponse.ok) {
				throw toHttpClientError(nextResponse.status, nextPayload);
			}
			return toSuccessEnvelope<TData>(nextPayload);
		}

		throw toHttpClientError(response.status, payload);
	}

	return toSuccessEnvelope<TData>(payload);
};

// One refresh at a time: refresh tokens are single-use, and presenting one twice is treated
// by the API as theft (the whole session is revoked). Concurrent 401s share this promise.
let refreshInFlight: Promise<string> | null = null;

const refreshAccessToken = (): Promise<string> => {
	refreshInFlight ??= (async () => {
		try {
			const refreshed = await request<{ access_token: string }>("POST", "/auth/refresh", {
				body: {},
			});
			const newAccessToken = refreshed.data.access_token;
			tokenRefreshedCallback?.(newAccessToken);
			return newAccessToken;
		} catch (err) {
			// Only a rejected refresh token ends the session; a 429, 5xx or network error
			// leaves it alone so the user can retry
			if (err instanceof HttpClientError && err.status === 401) {
				authFailureCallback?.();
			}
			throw err;
		} finally {
			refreshInFlight = null;
		}
	})();
	return refreshInFlight;
};

export const httpClient = {
	get: <TData>(path: string, options?: RequestOptions) =>
		request<TData>("GET", path, options),
	post: <TData>(path: string, body: unknown, options: RequestOptions = {}) =>
		request<TData>("POST", path, { ...options, body }),
	put: <TData>(path: string, body: unknown, options: RequestOptions = {}) =>
		request<TData>("PUT", path, { ...options, body }),
	patch: <TData>(path: string, body: unknown, options: RequestOptions = {}) =>
		request<TData>("PATCH", path, { ...options, body }),
	delete: <TData>(path: string, options?: RequestOptions) =>
		request<TData>("DELETE", path, options),
};
