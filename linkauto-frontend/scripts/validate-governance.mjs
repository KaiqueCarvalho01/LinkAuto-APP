#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import process from "node:process";

const frontendRoot = process.cwd();
const repoRoot = path.resolve(frontendRoot, "..");
const featureDir = path.join(repoRoot, "specs", "002-frontend-iterative-spec");
const iterationsDir = path.join(featureDir, "iterations");
const trackerPath = path.join(repoRoot, "progressTracker-frontend.md");
const endpointRequestsPath = path.join(featureDir, "endpoint-requests.md");

const errors = [];
const warnings = [];

function readText(filePath) {
	if (!fs.existsSync(filePath)) {
		errors.push(
			`Missing required file: ${path.relative(repoRoot, filePath)}`,
		);
		return "";
	}
	return fs.readFileSync(filePath, "utf8");
}

function hasTraceabilitySections(markdown) {
	const normalized = markdown.toLowerCase();
	const hasWhat =
		normalized.includes("what was delivered") ||
		normalized.includes("o que foi executado");
	const hasWhere =
		normalized.includes("where it was delivered") ||
		normalized.includes("onde foi executado") ||
		normalized.includes("arquivos/caminhos");
	const hasHow =
		normalized.includes("how it was validated") ||
		normalized.includes("como foi validado") ||
		normalized.includes("comandos e resultado");

	return { hasWhat, hasWhere, hasHow };
}

function validateIterationFiles() {
	if (!fs.existsSync(iterationsDir)) {
		errors.push(
			`Missing iterations directory: ${path.relative(repoRoot, iterationsDir)}`,
		);
		return;
	}

	const iterationFiles = fs
		.readdirSync(iterationsDir)
		.filter((name) => /^iteration-\d+\.md$/i.test(name));

	if (iterationFiles.length === 0) {
		errors.push(
			"No iteration-XXX.md file found in specs/002-frontend-iterative-spec/iterations",
		);
		return;
	}

	for (const name of iterationFiles) {
		const filePath = path.join(iterationsDir, name);
		const content = readText(filePath);
		if (!content) {
			continue;
		}

		if (!/scope_mode\s*:/i.test(content)) {
			errors.push(`${name}: missing scope_mode declaration`);
		}

		if (!/(TASK_BATCH|USER_STORY_FEATURE)/i.test(content)) {
			errors.push(
				`${name}: missing scope_mode value TASK_BATCH or USER_STORY_FEATURE`,
			);
		}

		if (!/acceptance_criteria\s*:/i.test(content)) {
			errors.push(`${name}: missing acceptance_criteria entries`);
		}

		if (!/(integration boundary|integration_boundary)/i.test(content)) {
			errors.push(`${name}: missing integration boundary section`);
		}

		const selectedItemsMatch = content.match(
			/selected_items_count\s*:\s*(\d+)/i,
		);
		if (selectedItemsMatch) {
			const count = Number.parseInt(selectedItemsMatch[1], 10);
			if (Number.isFinite(count) && count > 4) {
				errors.push(
					`${name}: selected_items_count exceeds max policy (4)`,
				);
			}
		}
	}
}

function validateTracker() {
	const tracker = readText(trackerPath);
	if (!tracker) {
		return;
	}

	const traceability = hasTraceabilitySections(tracker);
	if (
		!traceability.hasWhat ||
		!traceability.hasWhere ||
		!traceability.hasHow
	) {
		errors.push(
			"progressTracker-frontend.md must include what/where/how traceability sections",
		);
	}
}

function validateEndpointRequests() {
	const content = readText(endpointRequestsPath);
	if (!content) {
		return;
	}

	if (!/##\s+ER-XXX/i.test(content)) {
		warnings.push(
			"endpoint-requests.md should keep ER-XXX template available",
		);
	}
}

validateIterationFiles();
validateTracker();
validateEndpointRequests();

if (errors.length > 0) {
	console.error("Governance validation failed:");
	for (const error of errors) {
		console.error(`- ${error}`);
	}
	if (warnings.length > 0) {
		console.error("Warnings:");
		for (const warning of warnings) {
			console.error(`- ${warning}`);
		}
	}
	process.exit(1);
}

console.log("Governance validation passed.");
if (warnings.length > 0) {
	console.log("Warnings:");
	for (const warning of warnings) {
		console.log(`- ${warning}`);
	}
}
