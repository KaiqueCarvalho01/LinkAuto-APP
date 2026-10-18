import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { HttpClientError, httpClient, setOnAuthFailure, setOnTokenRefreshed } from "./httpClient";

const json = (status: number, body: unknown) =>
	new Response(JSON.stringify(body), {
		status,
		headers: { "content-type": "application/json" },
	});
const ok = (data: unknown) => json(200, { data, error: null, meta: {} });
const fail = (status: number, code: string, message: string) =>
	json(status, { data: null, error: { code, message }, meta: {} });

type Route = (init: RequestInit) => Response | Promise<Response>;

// Fake API: /auth/refresh is handled by `refresh`; other paths answer 200 to the new token
// and 401 to anything else, unless `retry` says otherwise
const mockApi = ({ refresh, retry }: { refresh: Route; retry?: Route }) => {
	const calls: string[] = [];
	vi.stubGlobal(
		"fetch",
		vi.fn(async (url: string, init: RequestInit) => {
			const path = new URL(url).pathname.replace(/^\/api\/v1/, "");
			calls.push(path);
			if (path === "/auth/refresh") return refresh(init);
			const auth = (init.headers as Record<string, string>).Authorization;
			if (auth !== "Bearer new") return fail(401, "UNAUTHORIZED", "expired");
			return retry ? retry(init) : ok({ path });
		}),
	);
	return calls;
};

describe("httpClient token refresh", () => {
	const onAuthFailure = vi.fn();
	const onTokenRefreshed = vi.fn();

	beforeEach(() => {
		setOnAuthFailure(onAuthFailure);
		setOnTokenRefreshed(onTokenRefreshed);
	});

	afterEach(() => {
		vi.unstubAllGlobals();
		vi.clearAllMocks();
	});

	it("shares one refresh between concurrent 401s (refresh tokens are single-use)", async () => {
		let resolveRefresh: (value: Response) => void = () => undefined;
		const calls = mockApi({
			refresh: () =>
				new Promise<Response>((resolve) => {
					resolveRefresh = resolve;
				}),
		});

		const both = Promise.all([
			httpClient.get<{ path: string }>("/admin/instructors", { token: "old" }),
			httpClient.get<{ path: string }>("/admin/stats", { token: "old" }),
		]);
		await vi.waitFor(() => {
			expect(calls).toContain("/auth/refresh");
		});
		resolveRefresh(ok({ access_token: "new" }));
		const [first, second] = await both;

		expect(calls.filter((path) => path === "/auth/refresh")).toHaveLength(1);
		expect(first.data.path).toBe("/admin/instructors");
		expect(second.data.path).toBe("/admin/stats");
		expect(onTokenRefreshed).toHaveBeenCalledTimes(1);
		expect(onTokenRefreshed).toHaveBeenCalledWith("new");
		expect(onAuthFailure).not.toHaveBeenCalled();
	});

	it("ends the session only when the refresh token is rejected", async () => {
		mockApi({ refresh: () => fail(401, "UNAUTHORIZED", "Invalid refresh token.") });

		await expect(httpClient.get("/users/me", { token: "old" })).rejects.toMatchObject({
			status: 401,
		});
		expect(onAuthFailure).toHaveBeenCalledTimes(1);
	});

	it.each([
		[429, "RATE_LIMIT_EXCEEDED"],
		[503, "HTTP_ERROR"],
	])("keeps the session when the refresh answers %i", async (status, code) => {
		mockApi({ refresh: () => fail(status, code, "try later") });

		await expect(httpClient.get("/users/me", { token: "old" })).rejects.toMatchObject({
			status,
		});
		expect(onAuthFailure).not.toHaveBeenCalled();
	});

	it("reports the retried request's own error, not the original 401", async () => {
		mockApi({
			refresh: () => ok({ access_token: "new" }),
			retry: () => fail(409, "CONFLICT", "Slot already booked"),
		});

		const error = await httpClient.post("/bookings", {}, { token: "old" }).catch((e) => e);

		expect(error).toBeInstanceOf(HttpClientError);
		expect(error).toMatchObject({ status: 409, message: "Slot already booked" });
		expect(onAuthFailure).not.toHaveBeenCalled();
	});

	it("keeps the session when the retry hits a network error", async () => {
		mockApi({
			refresh: () => ok({ access_token: "new" }),
			retry: () => {
				throw new TypeError("Failed to fetch");
			},
		});

		await expect(httpClient.get("/users/me", { token: "old" })).rejects.toThrow(
			"Failed to fetch",
		);
		expect(onAuthFailure).not.toHaveBeenCalled();
	});
});
