export interface ChecklistStats {
	total: number;
	completed: number;
	incomplete: number;
}

export interface MarkdownLogRecord {
	path: string;
	raw: string;
	lines: string[];
	headings: string[];
	checklist: ChecklistStats;
}

export interface TraceabilitySectionsResult {
	hasWhat: boolean;
	hasWhere: boolean;
	hasHow: boolean;
	missing: string[];
}

function normalizeLines(markdown: string): string[] {
	return markdown.replace(/\r/g, "").split("\n");
}

function parseChecklist(lines: string[]): ChecklistStats {
	let total = 0;
	let completed = 0;

	for (const line of lines) {
		if (/^- \[( |x|X)\]/.test(line)) {
			total += 1;
			if (/^- \[(x|X)\]/.test(line)) {
				completed += 1;
			}
		}
	}

	return {
		total,
		completed,
		incomplete: total - completed,
	};
}

function parseHeadings(lines: string[]): string[] {
	const headings: string[] = [];

	for (const line of lines) {
		const match = line.match(/^#{1,6}\s+(.+)$/);
		if (!match) {
			continue;
		}
		const headingText = match[1];
		if (!headingText) {
			continue;
		}

		headings.push(headingText.trim());
	}

	return headings;
}

export function createMarkdownLogRecord(
	path: string,
	markdown: string,
): MarkdownLogRecord {
	const lines = normalizeLines(markdown);

	return {
		path,
		raw: markdown,
		lines,
		headings: parseHeadings(lines),
		checklist: parseChecklist(lines),
	};
}

export function evaluateTraceabilitySections(
	markdown: string,
): TraceabilitySectionsResult {
	const normalized = markdown.replace(/\r/g, "").toLowerCase();

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

	const missing: string[] = [];
	if (!hasWhat) {
		missing.push("what was delivered");
	}
	if (!hasWhere) {
		missing.push("where it was delivered");
	}
	if (!hasHow) {
		missing.push("how it was validated");
	}

	return {
		hasWhat,
		hasWhere,
		hasHow,
		missing,
	};
}
