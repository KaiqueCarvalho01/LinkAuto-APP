import { describe, expect, it } from "vitest";

import { validateRedGreenEvidence } from "./qualityGate";

describe("qualityGate", () => {
	it("accepts valid red-green evidence when red happens before green", () => {
		const result = validateRedGreenEvidence({
			taskId: "T021",
			redCommand:
				"npm run test -- src/features/iteration-governance/qualityGate.test.ts",
			redFailureSummary: "fails because validator is missing",
			redCapturedAt: "2026-04-22T09:00:00.000Z",
			greenCommand:
				"npm run test -- src/features/iteration-governance/qualityGate.test.ts",
			greenSuccessSummary: "passes after implementing validator",
			greenCapturedAt: "2026-04-22T09:03:00.000Z",
		});

		expect(result.isValid).toBe(true);
		expect(result.errors).toEqual([]);
	});

	it("rejects evidence missing mandatory red fields", () => {
		const result = validateRedGreenEvidence({
			taskId: "T021",
			redCommand: "",
			redFailureSummary: "",
			greenCommand: "",
			greenSuccessSummary: "",
		});

		expect(result.isValid).toBe(false);
		expect(result.errors).toContain("redCommand is required");
		expect(result.errors).toContain("redFailureSummary is required");
		expect(result.errors).toContain("greenCommand is required");
		expect(result.errors).toContain("greenSuccessSummary is required");
	});

	it("rejects evidence when green timestamp is before red timestamp", () => {
		const result = validateRedGreenEvidence({
			taskId: "T021",
			redCommand:
				"npm run test -- src/features/iteration-governance/qualityGate.test.ts",
			redFailureSummary: "fails because validator is missing",
			redCapturedAt: "2026-04-22T09:05:00.000Z",
			greenCommand:
				"npm run test -- src/features/iteration-governance/qualityGate.test.ts",
			greenSuccessSummary: "passes after implementing validator",
			greenCapturedAt: "2026-04-22T09:03:00.000Z",
		});

		expect(result.isValid).toBe(false);
		expect(result.errors).toContain(
			"redCapturedAt must be earlier than greenCapturedAt",
		);
	});

	it("rejects evidence with invalid timestamp values", () => {
		const result = validateRedGreenEvidence({
			taskId: "T021",
			redCommand:
				"npm run test -- src/features/iteration-governance/qualityGate.test.ts",
			redFailureSummary: "fails because validator is missing",
			redCapturedAt: "not-a-date",
			greenCommand:
				"npm run test -- src/features/iteration-governance/qualityGate.test.ts",
			greenSuccessSummary: "passes after implementing validator",
			greenCapturedAt: "2026-04-22T09:03:00.000Z",
		});

		expect(result.isValid).toBe(false);
		expect(result.errors).toContain(
			"timestamps must be valid ISO date values",
		);
	});
});
