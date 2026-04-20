import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterEach } from "vitest";

afterEach(() => {
	cleanup();
});

class ResizeObserverMock {
	observe() {
		return undefined;
	}

	unobserve() {
		return undefined;
	}

	disconnect() {
		return undefined;
	}
}

if (!globalThis.ResizeObserver) {
	globalThis.ResizeObserver = ResizeObserverMock as typeof ResizeObserver;
}
