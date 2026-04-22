export interface CoverageMetrics {
	lines: number;
	branches: number;
	functions: number;
	statements: number;
}

export interface CoveragePolicyInput {
	threshold?: number;
	metrics: CoverageMetrics;
}

export type CoverageMetricName = keyof CoverageMetrics;

export interface CoveragePolicyResult {
	passed: boolean;
	failingMetrics: CoverageMetricName[];
	errors: string[];
}

const METRIC_NAMES: CoverageMetricName[] = [
	"lines",
	"branches",
	"functions",
	"statements",
];

export function validateCoverageThreshold(
	input: CoveragePolicyInput,
): CoveragePolicyResult {
	const threshold = input.threshold ?? 80;
	const errors: string[] = [];
	const failingMetrics: CoverageMetricName[] = [];

	for (const metricName of METRIC_NAMES) {
		const metricValue = input.metrics[metricName];

		if (
			!Number.isFinite(metricValue) ||
			metricValue < 0 ||
			metricValue > 100
		) {
			errors.push(`${metricName} must be between 0 and 100`);
			continue;
		}

		if (metricValue < threshold) {
			failingMetrics.push(metricName);
			errors.push(`${metricName} is below threshold ${threshold}`);
		}
	}

	return {
		passed: errors.length === 0,
		failingMetrics,
		errors,
	};
}
