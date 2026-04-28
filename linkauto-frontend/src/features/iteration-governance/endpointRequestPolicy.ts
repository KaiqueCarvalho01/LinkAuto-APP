export type EndpointRequestStatus =
	| "PROPOSED"
	| "IN_REVIEW"
	| "APPROVED"
	| "REJECTED"
	| "POSTPONED";

export interface EndpointRequestPolicyInput {
	newEndpointRequired: boolean;
	requestId?: string;
	requestStatus?: EndpointRequestStatus;
}

export interface EndpointRequestPolicyResult {
	isValid: boolean;
	errors: string[];
}

function hasValue(value: string | undefined): boolean {
	return Boolean(value && value.trim().length > 0);
}

export function validateEndpointRequestPrerequisite(
	input: EndpointRequestPolicyInput,
): EndpointRequestPolicyResult {
	const errors: string[] = [];

	if (!input.newEndpointRequired) {
		return { isValid: true, errors };
	}

	if (!hasValue(input.requestId)) {
		errors.push("requestId is mandatory when newEndpointRequired is true");
	}

	if (input.requestStatus !== "APPROVED") {
		errors.push(
			"Endpoint request must be APPROVED to proceed with integration",
		);
	}

	return {
		isValid: errors.length === 0,
		errors,
	};
}
