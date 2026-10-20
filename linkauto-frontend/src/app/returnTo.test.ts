import { describe, expect, it } from "vitest";

import { returnToFrom } from "./returnTo";

describe("returnToFrom", () => {
	it("returns the path, query and hash the visitor was sent away from", () => {
		expect(
			returnToFrom({ from: { pathname: "/my-lessons", search: "?status=PENDENTE", hash: "#top" } }),
		).toEqual({ path: "/my-lessons?status=PENDENTE#top", state: undefined });
	});

	it("keeps the navigation state of that page", () => {
		const instructor = { slug: "marcos-lima" };
		expect(
			returnToFrom({ from: { pathname: "/bookings/new", state: { instructor } } }),
		).toEqual({ path: "/bookings/new", state: { instructor } });
	});

	it.each([
		["no state", null],
		["no from", { other: true }],
		["a non-string pathname", { from: { pathname: 42 } }],
		["a relative path", { from: { pathname: "my-lessons" } }],
		["a protocol-relative URL", { from: { pathname: "//evil.example" } }],
		["the login page itself", { from: { pathname: "/login" } }],
	])("ignores %s", (_, state) => {
		expect(returnToFrom(state)).toBeNull();
	});
});
