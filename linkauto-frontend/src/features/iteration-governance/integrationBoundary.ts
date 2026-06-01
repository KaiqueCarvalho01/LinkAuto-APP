export type ContractStatus = "CONTRACTED" | "NOT_CONTRACTED";
export type IntegrationAction = "USE_CONTRACT" | "USE_MOCK";

export interface IntegrationBoundaryInput {
	capability: string;
	contractStatus: ContractStatus;
	fallbackStrategy?: string;
	endpointReference?: string;
}

export interface IntegrationBoundaryResult {
	isValid: boolean;
	action?: IntegrationAction;
	strategy?: string;
	reference?: string;
	errors: string[];
}

function hasValue(value: string | undefined): boolean {
	return Boolean(value && value.trim().length > 0);
}

export function resolveIntegrationBoundary(
	input: IntegrationBoundaryInput,
): IntegrationBoundaryResult {
	const errors: string[] = [];

	if (input.contractStatus === "NOT_CONTRACTED") {
		if (!hasValue(input.fallbackStrategy)) {
			errors.push(
				"fallbackStrategy is required for NOT_CONTRACTED capabilities",
			);
		}
		if (errors.length > 0) {
			return { isValid: false, errors };
		}
		const result: IntegrationBoundaryResult = {
			isValid: true,
			action: "USE_MOCK",
			errors,
		};
		if (input.fallbackStrategy) {
			result.strategy = input.fallbackStrategy;
		}
		return result;
	}

	if (input.contractStatus === "CONTRACTED") {
		if (!hasValue(input.endpointReference)) {
			errors.push(
				"endpointReference is required for CONTRACTED capabilities",
			);
		}
		if (errors.length > 0) {
			return { isValid: false, errors };
		}
		const result: IntegrationBoundaryResult = {
			isValid: true,
			action: "USE_CONTRACT",
			errors,
		};
		if (input.endpointReference) {
			result.reference = input.endpointReference;
		}
		return result;
	}

	errors.push("contractStatus must be CONTRACTED or NOT_CONTRACTED");
	return { isValid: false, errors };
}
