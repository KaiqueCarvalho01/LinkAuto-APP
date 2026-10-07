import { act, renderHook } from "@testing-library/react";
import type { ReactNode } from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { SessionProvider, useSessionStore } from "./sessionStore";

const SESSION_STORAGE_KEY = "linkauto.session.v1";

const wrapper = ({ children }: { children: ReactNode }) => (
	<SessionProvider>{children}</SessionProvider>
);

// Isolated in-memory Storage: recent Node versions define their own global localStorage,
// which can shadow jsdom's and is unavailable without --localstorage-file.
const createMemoryStorage = (): Storage => {
	const items = new Map<string, string>();
	return {
		get length() {
			return items.size;
		},
		clear: () => items.clear(),
		getItem: (key) => items.get(key) ?? null,
		key: (index) => [...items.keys()][index] ?? null,
		removeItem: (key) => {
			items.delete(key);
		},
		setItem: (key, value) => {
			items.set(key, String(value));
		},
	};
};

describe("sessionStore.signOut", () => {
	beforeEach(() => {
		vi.stubGlobal("localStorage", createMemoryStorage());
		localStorage.setItem(
			SESSION_STORAGE_KEY,
			JSON.stringify({
				accessToken: "access-token",
				tokenType: "bearer",
				user: { email: "aluno@linkauto.com.br", roles: ["ALUNO"] },
			}),
		);
	});

	afterEach(() => {
		vi.unstubAllGlobals();
	});

	it("revokes the refresh token on the server and clears the session", async () => {
		const fetchMock = vi.fn().mockResolvedValue(new Response(null, { status: 204 }));
		vi.stubGlobal("fetch", fetchMock);
		const { result } = renderHook(() => useSessionStore(), { wrapper });
		expect(result.current.isAuthenticated).toBe(true);

		await act(async () => {
			await result.current.signOut();
		});

		expect(fetchMock).toHaveBeenCalledTimes(1);
		const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit];
		expect(url).toMatch(/\/auth\/logout$/);
		expect(init.method).toBe("POST");
		expect(init.credentials).toBe("include");
		expect(result.current.isAuthenticated).toBe(false);
		expect(localStorage.getItem(SESSION_STORAGE_KEY)).toBeNull();
	});

	it("clears the local session even if the logout request fails", async () => {
		vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("offline")));
		const { result } = renderHook(() => useSessionStore(), { wrapper });

		await act(async () => {
			await result.current.signOut();
		});

		expect(result.current.isAuthenticated).toBe(false);
		expect(localStorage.getItem(SESSION_STORAGE_KEY)).toBeNull();
	});
});
