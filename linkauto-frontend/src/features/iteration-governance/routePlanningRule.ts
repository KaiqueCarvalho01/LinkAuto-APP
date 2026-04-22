export type PlanningTaskType = "ROUTE_SCAFFOLD" | "UI_FINAL" | "OTHER";

export interface PlanningTask {
	id: string;
	type: PlanningTaskType;
	order: number;
}

export interface RoutePlanningResult {
	isValid: boolean;
	violations: string[];
}

export function validateRouteScaffoldOrder(
	tasks: PlanningTask[],
): RoutePlanningResult {
	const violations: string[] = [];

	if (tasks.length === 0) {
		return {
			isValid: true,
			violations,
		};
	}

	const sortedTasks = [...tasks].sort((a, b) => a.order - b.order);
	const firstUiFinal = sortedTasks.find((task) => task.type === "UI_FINAL");
	if (!firstUiFinal) {
		return {
			isValid: true,
			violations,
		};
	}

	const scaffoldTasks = sortedTasks.filter(
		(task) => task.type === "ROUTE_SCAFFOLD",
	);
	if (scaffoldTasks.length === 0) {
		violations.push(
			"UI_FINAL tasks require a ROUTE_SCAFFOLD task beforehand",
		);
		return {
			isValid: false,
			violations,
		};
	}

	const earliestScaffold = scaffoldTasks[0];
	if (!earliestScaffold) {
		violations.push(
			"UI_FINAL tasks require a ROUTE_SCAFFOLD task beforehand",
		);
		return {
			isValid: false,
			violations,
		};
	}

	if (earliestScaffold.order >= firstUiFinal.order) {
		violations.push("ROUTE_SCAFFOLD must be ordered before UI_FINAL tasks");
	}

	return {
		isValid: violations.length === 0,
		violations,
	};
}
