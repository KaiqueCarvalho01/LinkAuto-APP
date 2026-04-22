export interface RedGreenEvidenceInput {
	taskId: string;
	redCommand: string;
	redFailureSummary: string;
	greenCommand: string;
	greenSuccessSummary: string;
	redCapturedAt?: string;
	greenCapturedAt?: string;
}

export interface RedGreenEvidenceResult {
	isValid: boolean;
	errors: string[];
}

function hasValue(value: string | undefined): boolean {
	return Boolean(value && value.trim().length > 0);
}

export function validateRedGreenEvidence(
	input: RedGreenEvidenceInput,
): RedGreenEvidenceResult {
	const errors: string[] = [];

	if (!hasValue(input.taskId)) {
		errors.push("taskId is required");
	}
	if (!hasValue(input.redCommand)) {
		errors.push("redCommand is required");
	}
	if (!hasValue(input.redFailureSummary)) {
		errors.push("redFailureSummary is required");
	}
	if (!hasValue(input.greenCommand)) {
		errors.push("greenCommand is required");
	}
	if (!hasValue(input.greenSuccessSummary)) {
		errors.push("greenSuccessSummary is required");
	}

	if (input.redCapturedAt && input.greenCapturedAt) {
		const redTime = Date.parse(input.redCapturedAt);
		const greenTime = Date.parse(input.greenCapturedAt);
		if (!Number.isNaN(redTime) && !Number.isNaN(greenTime)) {
			if (redTime >= greenTime) {
				errors.push(
					"redCapturedAt must be earlier than greenCapturedAt",
				);
			}
		} else {
			errors.push("timestamps must be valid ISO date values");
		}
	}

	return {
		isValid: errors.length === 0,
		errors,
	};
}
