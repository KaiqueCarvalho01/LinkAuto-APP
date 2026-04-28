import { describe, expect, it } from "vitest";

import { validateRouteScaffoldOrder } from "./routePlanningRule";

describe("routePlanningRule", () => {
	it("accepts route scaffold before final UI task", () => {
		const result = validateRouteScaffoldOrder([
			{ id: "task-1", type: "ROUTE_SCAFFOLD", order: 1 },
			{ id: "task-2", type: "UI_FINAL", order: 2 },
		]);

		expect(result.isValid).toBe(true);
		expect(result.violations).toEqual([]);
	});

	it("rejects final UI task when scaffold route is missing", () => {
		const result = validateRouteScaffoldOrder([
			{ id: "task-2", type: "UI_FINAL", order: 2 },
		]);

		expect(result.isValid).toBe(false);
		expect(result.violations).toContain(
			"UI_FINAL tasks require a ROUTE_SCAFFOLD task beforehand",
		);
	});

	it("rejects final UI task when scaffold comes after UI task", () => {
		const result = validateRouteScaffoldOrder([
			{ id: "task-2", type: "UI_FINAL", order: 2 },
			{ id: "task-3", type: "ROUTE_SCAFFOLD", order: 3 },
		]);

		expect(result.isValid).toBe(false);
		expect(result.violations).toContain(
			"ROUTE_SCAFFOLD must be ordered before UI_FINAL tasks",
		);
	});
});
