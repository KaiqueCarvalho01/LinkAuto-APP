import type { Location } from "react-router-dom";

export interface ReturnTo {
	readonly path: string;
	readonly state: unknown;
}

// Where to go after login: the page a guard sent the visitor away from (`state.from`).
// Only paths inside the app are accepted.
export const returnToFrom = (state: unknown): ReturnTo | null => {
	const from = (state as { from?: Partial<Location> } | null)?.from;
	const pathname = from?.pathname;
	if (typeof pathname !== "string") return null;
	if (!pathname.startsWith("/") || pathname.startsWith("//") || pathname === "/login") {
		return null;
	}
	return {
		path: `${pathname}${from?.search ?? ""}${from?.hash ?? ""}`,
		state: from?.state,
	};
};
