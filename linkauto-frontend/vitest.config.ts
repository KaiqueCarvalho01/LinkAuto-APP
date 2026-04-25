import { configDefaults, defineConfig } from "vitest/config";

export default defineConfig({
	test: {
		environment: "jsdom",
		setupFiles: "./src/test/setup.ts",
		css: true,
		exclude: [...configDefaults.exclude, "tests/e2e/**"],
		coverage: {
			provider: "v8",
			reporter: ["text", "html"],
			include: [
				"src/components/BookingStatusBadge.tsx",
				"src/components/SlotPicker.tsx",
				"src/components/Navbar.tsx",
				"src/components/ProfileSidebar.tsx",
				"src/components/landing/*.tsx",
				"src/features/**/*.{ts,tsx}",
				"src/pages/Login.tsx",
				"src/pages/Register.tsx",
				"src/pages/LessonDetails.tsx",
			],
			exclude: ["src/main.tsx", "src/app/router.tsx"],
			thresholds: {
				lines: 70,
				functions: 70,
				branches: 65,
				statements: 70,
			},
		},
	},
});
