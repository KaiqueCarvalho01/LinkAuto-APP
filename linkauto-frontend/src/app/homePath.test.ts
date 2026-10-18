import { describe, expect, it } from "vitest";

import { homePathFor } from "./homePath";

describe("homePathFor", () => {
	it.each([
		[["ADMIN"], undefined, "/admin/instructors"],
		[["ALUNO"], undefined, "/search"],
		[["ALUNO"], "instructor" as const, "/search"],
		[["INSTRUTOR"], undefined, "/instructor/dashboard"],
		[["INSTRUTOR"], "student" as const, "/instructor/dashboard"],
		[["ALUNO", "INSTRUTOR"], "student" as const, "/search"],
		[["ALUNO", "INSTRUTOR"], "instructor" as const, "/instructor/dashboard"],
		[["ALUNO", "INSTRUTOR"], undefined, "/instructor/dashboard"],
		[[], undefined, "/profile"],
	])("sends %j (signed in as %s) to %s", (roles, preferred, expected) => {
		expect(homePathFor(roles, preferred)).toBe(expected);
	});
});
