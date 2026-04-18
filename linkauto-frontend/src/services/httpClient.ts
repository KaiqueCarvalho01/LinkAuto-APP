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
		const typedPayload = isApiErrorEnvelope(payload) ? payload : null;
		const fallback = `HTTP ${response.status}`;
		const message = typedPayload?.error.message || fallback;
		throw new HttpClientError(message, response.status, typedPayload);
	}

	if (payload === null) {
		return {
			data: null as TData,
			error: null,
			meta: {},
		};
	}

	return payload as ApiSuccessEnvelope<TData>;
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
