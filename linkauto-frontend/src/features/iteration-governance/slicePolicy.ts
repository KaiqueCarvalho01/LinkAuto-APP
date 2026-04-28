export type ScopeMode = "TASK_BATCH" | "USER_STORY_FEATURE";

export interface SlicePolicyInput {
	scopeMode: ScopeMode;
	selectedItemsCount: number;
}

export interface SlicePolicyResult {
	isValid: boolean;
	errors: string[];
}

export function validateSlicePolicy(
	input: SlicePolicyInput,
): SlicePolicyResult {
	const errors: string[] = [];

	if (
		!Number.isInteger(input.selectedItemsCount) ||
		input.selectedItemsCount < 1
	) {
		errors.push("selectedItemsCount must be a positive integer");
	}

	if (
		input.scopeMode === "TASK_BATCH" &&
		(input.selectedItemsCount < 1 || input.selectedItemsCount > 4)
	) {
		errors.push("TASK_BATCH supports only 1 to 4 items");
	}

	if (
		input.scopeMode === "USER_STORY_FEATURE" &&
		input.selectedItemsCount !== 1
	) {
		errors.push(
			"USER_STORY_FEATURE must contain exactly one selected item",
		);
	}

	return {
		isValid: errors.length === 0,
		errors,
	};
}
