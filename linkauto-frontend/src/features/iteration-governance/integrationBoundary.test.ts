import { describe, expect, it } from "vitest";

import { resolveIntegrationBoundary } from "./integrationBoundary";

describe("integrationBoundary", () => {
	it("returns explicit fallback action when capability is NOT_CONTRACTED", () => {
		const result = resolveIntegrationBoundary({
			capability: "Instructor Search",
			contractStatus: "NOT_CONTRACTED",
			fallbackStrategy: "Use local mock data in search-service",
		});

		expect(result.isValid).toBe(true);
		expect(result.action).toBe("USE_MOCK");
		expect(result.strategy).toBe("Use local mock data in search-service");
	});

	it("returns use contract action when capability is CONTRACTED and reference exists", () => {
		const result = resolveIntegrationBoundary({
			capability: "Instructor Search",
			contractStatus: "CONTRACTED",
			endpointReference: "GET /api/v1/instructors",
		});

		expect(result.isValid).toBe(true);
		expect(result.action).toBe("USE_CONTRACT");
		expect(result.reference).toBe("GET /api/v1/instructors");
	});

	it("rejects NOT_CONTRACTED capability if no fallback strategy is defined", () => {
		const result = resolveIntegrationBoundary({
			capability: "Instructor Search",
			contractStatus: "NOT_CONTRACTED",
			fallbackStrategy: "",
		});

		expect(result.isValid).toBe(false);
		expect(result.errors).toContain(
			"fallbackStrategy is required for NOT_CONTRACTED capabilities",
		);
	});

	it("rejects CONTRACTED capability if no endpoint reference is defined", () => {
		const result = resolveIntegrationBoundary({
			capability: "Instructor Search",
			contractStatus: "CONTRACTED",
			endpointReference: "",
		});

		expect(result.isValid).toBe(false);
		expect(result.errors).toContain(
			"endpointReference is required for CONTRACTED capabilities",
		);
	});
});
