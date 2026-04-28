import { describe, expect, it } from "vitest";

import {
	createMarkdownLogRecord,
	evaluateTraceabilitySections,
} from "./logLoader";

describe("logLoader", () => {
	it("builds checklist stats from markdown content", () => {
		const markdown = [
			"# Execution",
			"- [x] completed item",
			"- [ ] pending item",
			"- [X] completed item 2",
		].join("\n");

		const record = createMarkdownLogRecord(
			"specs/002-frontend-iterative-spec/iterations/iteration-001.md",
			markdown,
		);

		expect(record.path).toBe(
			"specs/002-frontend-iterative-spec/iterations/iteration-001.md",
		);
		expect(record.checklist.total).toBe(3);
		expect(record.checklist.completed).toBe(2);
		expect(record.checklist.incomplete).toBe(1);
		expect(record.headings).toEqual(["Execution"]);
	});

	it("normalizes lines and detects required traceability sections", () => {
		const markdown = [
			"## What was delivered\r",
			"item 1\r",
			"## Where it was delivered\r",
			"path 1\r",
			"## How it was validated\r",
			"npm run test\r",
		].join("\n");

		const result = evaluateTraceabilitySections(markdown);

		expect(result.hasWhat).toBe(true);
		expect(result.hasWhere).toBe(true);
		expect(result.hasHow).toBe(true);
		expect(result.missing).toEqual([]);
	});

	it("reports missing traceability sections", () => {
		const markdown = ["## What was delivered", "item 1"].join("\n");

		const result = evaluateTraceabilitySections(markdown);

		expect(result.hasWhat).toBe(true);
		expect(result.hasWhere).toBe(false);
		expect(result.hasHow).toBe(false);
		expect(result.missing).toEqual([
			"where it was delivered",
			"how it was validated",
		]);
	});
});
