import { describe, expect, it } from "vitest";

import { validateEndpointRequestPrerequisite } from "./endpointRequestPolicy";

describe("endpointRequestPolicy", () => {
	it("accepts implementation if no new endpoint is required", () => {
		const result = validateEndpointRequestPrerequisite({
			newEndpointRequired: false,
		});

		expect(result.isValid).toBe(true);
		expect(result.errors).toEqual([]);
	});

	it("accepts implementation if new endpoint is required AND explicitly referenced", () => {
		const result = validateEndpointRequestPrerequisite({
			newEndpointRequired: true,
			requestId: "ER-001",
			requestStatus: "APPROVED",
		});

		expect(result.isValid).toBe(true);
		expect(result.errors).toEqual([]);
	});

	it("rejects implementation if new endpoint is required but no request ID is provided", () => {
		const result = validateEndpointRequestPrerequisite({
			newEndpointRequired: true,
			requestId: "",
		});

		expect(result.isValid).toBe(false);
		expect(result.errors).toContain(
			"requestId is mandatory when newEndpointRequired is true",
		);
	});

	it("rejects implementation if endpoint request exists but status is PROPOSED or REJECTED", () => {
		const result = validateEndpointRequestPrerequisite({
			newEndpointRequired: true,
			requestId: "ER-002",
			requestStatus: "REJECTED",
		});

		expect(result.isValid).toBe(false);
		expect(result.errors).toContain(
			"Endpoint request must be APPROVED to proceed with integration",
		);
	});
});
