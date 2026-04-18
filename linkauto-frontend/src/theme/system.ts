import { createSystem, defaultConfig, defineConfig } from "@chakra-ui/react";

const config = defineConfig({
	globalCss: {
		"html, body": {
			minHeight: "100%",
		},
		body: {
			bgGradient: "linear(145deg, #f4f8fc 0%, #edf5ff 45%, #f8fbff 100%)",
			color: "ink.800",
		},
		"*::selection": {
			bg: "brand.200",
			color: "ink.900",
		},
	},
	theme: {
		tokens: {
			colors: {
				brand: {
					50: { value: "#e7f5ff" },
					100: { value: "#c8e7ff" },
					200: { value: "#9dd4ff" },
					300: { value: "#72c1ff" },
					400: { value: "#49abf4" },
					500: { value: "#2f87cc" },
					600: { value: "#236ea8" },
					700: { value: "#1a567f" },
					800: { value: "#133e5d" },
					900: { value: "#0f2f47" },
				},
				accent: {
					50: { value: "#ecfaed" },
					100: { value: "#c9efcb" },
					200: { value: "#a4e4a8" },
					300: { value: "#7bd783" },
					400: { value: "#58c864" },
					500: { value: "#44ad4f" },
					600: { value: "#338640" },
					700: { value: "#276834" },
					800: { value: "#1d4b27" },
					900: { value: "#173d20" },
				},
				ink: {
					50: { value: "#f4f6f8" },
					100: { value: "#e4e8ed" },
					200: { value: "#c7d1dc" },
					300: { value: "#a5b4c2" },
					400: { value: "#7f91a3" },
					500: { value: "#607489" },
					600: { value: "#46596c" },
					700: { value: "#2f3f4f" },
					800: { value: "#1f2c38" },
					900: { value: "#141d26" },
				},
			},
			fonts: {
				heading: { value: "'Sora', system-ui, sans-serif" },
				body: { value: "'Manrope', system-ui, sans-serif" },
			},
			radii: {
				xl: { value: "1rem" },
				"2xl": { value: "1.5rem" },
				"3xl": { value: "2rem" },
			},
		},
		semanticTokens: {
			colors: {
				surface: {
					canvas: { value: "#f4f8fc" },
					panel: { value: "#ffffff" },
					hero: { value: "#0f2f47" },
				},
				brand: {
					solid: { value: "{colors.brand.600}" },
					muted: { value: "{colors.brand.100}" },
					focusRing: { value: "{colors.brand.500}" },
				},
				accent: {
					solid: { value: "{colors.accent.500}" },
					muted: { value: "{colors.accent.100}" },
				},
			},
		},
	},
});

export const appSystem = createSystem(defaultConfig, config);
