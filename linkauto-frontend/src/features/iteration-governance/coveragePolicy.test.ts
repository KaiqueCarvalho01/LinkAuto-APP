import { describe, expect, it } from "vitest";

import { validateCoverageThreshold } from "./coveragePolicy";

describe("coveragePolicy", () => {
	it("accepts changed-scope coverage when all metrics meet threshold", () => {
		const result = validateCoverageThreshold({
			threshold: 80,
			metrics: {
				lines: 92,
				branches: 84,
				functions: 90,
				statements: 91,
			},
		});

		expect(result.passed).toBe(true);
		expect(result.failingMetrics).toEqual([]);
	});

	it("rejects changed-scope coverage when one or more metrics are below threshold", () => {
		const result = validateCoverageThreshold({
			threshold: 80,
			metrics: {
				lines: 92,
				branches: 76,
				functions: 90,
				statements: 79,
			},
		});

		expect(result.passed).toBe(false);
		expect(result.failingMetrics).toEqual(["branches", "statements"]);
		expect(result.errors).toContain("branches is below threshold 80");
		expect(result.errors).toContain("statements is below threshold 80");
	});

	it("rejects invalid metric values outside 0..100", () => {
		const result = validateCoverageThreshold({
			threshold: 80,
			metrics: {
				lines: 101,
				branches: -1,
				functions: 90,
				statements: 91,
			},
		});

		expect(result.passed).toBe(false);
		expect(result.errors).toContain("lines must be between 0 and 100");
		expect(result.errors).toContain("branches must be between 0 and 100");
	});
});
