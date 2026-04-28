import { describe, expect, it } from "vitest";

import { validateSlicePolicy } from "./slicePolicy";

describe("slicePolicy", () => {
	it("accepts TASK_BATCH with up to four selected items", () => {
		const result = validateSlicePolicy({
			scopeMode: "TASK_BATCH",
			selectedItemsCount: 4,
		});

		expect(result.isValid).toBe(true);
		expect(result.errors).toEqual([]);
	});

	it("rejects TASK_BATCH with more than four selected items", () => {
		const result = validateSlicePolicy({
			scopeMode: "TASK_BATCH",
			selectedItemsCount: 5,
		});

		expect(result.isValid).toBe(false);
		expect(result.errors).toContain(
			"TASK_BATCH supports only 1 to 4 items",
		);
	});

	it("rejects USER_STORY_FEATURE with item count different from one", () => {
		const result = validateSlicePolicy({
			scopeMode: "USER_STORY_FEATURE",
			selectedItemsCount: 2,
		});

		expect(result.isValid).toBe(false);
		expect(result.errors).toContain(
			"USER_STORY_FEATURE must contain exactly one selected item",
		);
	});
});
