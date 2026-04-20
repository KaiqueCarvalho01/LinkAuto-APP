import { createSystem, defaultConfig, defineConfig } from "@chakra-ui/react";

const config = defineConfig({
	globalCss: {
		"html, body": {
			minHeight: "100%",
		},
		body: {
			bg: "surface.canvas",
			color: "text.primary",
			fontFamily: "body",
			backgroundImage: {
				base: "radial-gradient(circle at 100% 0%, rgba(26, 109, 181, 0.08) 0%, rgba(26, 109, 181, 0) 36%), radial-gradient(circle at 0% 100%, rgba(62, 170, 91, 0.08) 0%, rgba(62, 170, 91, 0) 35%)",
				_dark: "radial-gradient(circle at 100% 0%, rgba(26, 109, 181, 0.24) 0%, rgba(26, 109, 181, 0) 38%), radial-gradient(circle at 0% 100%, rgba(62, 170, 91, 0.2) 0%, rgba(62, 170, 91, 0) 36%)",
			},
			backgroundAttachment: "fixed",
		},
		"*::selection": {
			bg: "brand.muted",
			color: "text.primary",
		},
		"input::placeholder, textarea::placeholder": {
			color: "text.muted",
			opacity: 1,
		},
		"input:-webkit-autofill, input:-webkit-autofill:hover, input:-webkit-autofill:focus, textarea:-webkit-autofill":
			{
				WebkitTextFillColor: "var(--chakra-colors-text-primary)",
				boxShadow:
					"inset 0 0 0 1000px var(--chakra-colors-surface-panel)",
				transition: "background-color 5000s ease-in-out 0s",
				caretColor: "var(--chakra-colors-text-primary)",
			},
	},
	theme: {
		tokens: {
			colors: {
				laBlue: {
					50: { value: "#EBF4FC" },
					100: { value: "#D6E8F7" },
					200: { value: "#B7D6F0" },
					300: { value: "#8ABCE2" },
					400: { value: "#4D92CA" },
					500: { value: "#1A6DB5" },
					600: { value: "#165E9C" },
					700: { value: "#124E87" },
				},
				laGreen: {
					50: { value: "#EAF6EF" },
					100: { value: "#D4EFE0" },
					200: { value: "#B8E4CA" },
					300: { value: "#8ED4A8" },
					400: { value: "#61BE81" },
					500: { value: "#3EAA5B" },
					600: { value: "#35924D" },
					700: { value: "#2C7D42" },
				},
				laGray: {
					50: { value: "#F9FAFB" },
					100: { value: "#F3F4F6" },
					200: { value: "#E5E7EB" },
					300: { value: "#D1D5DB" },
					400: { value: "#9CA3AF" },
					500: { value: "#6B7280" },
					600: { value: "#4B5563" },
					700: { value: "#374151" },
					800: { value: "#1F2937" },
					900: { value: "#111827" },
				},
				laStatus: {
					pending: { value: "#F59E0B" },
					confirmed: { value: "#1A6DB5" },
					completed: { value: "#3EAA5B" },
					cancelled: { value: "#EF4444" },
					blocked: { value: "#9CA3AF" },
				},
				surface: {
					canvas: { value: "#F8FAFC" },
					panel: { value: "#FFFFFF" },
					muted: { value: "#F3F4F6" },
					info: { value: "#D6E8F7" },
					success: { value: "#D4EFE0" },
				},
				brand: {
					50: { value: "#EBF4FC" },
					100: { value: "#D6E8F7" },
					200: { value: "#B7D6F0" },
					300: { value: "#8ABCE2" },
					400: { value: "#4D92CA" },
					500: { value: "#1A6DB5" },
					600: { value: "#165E9C" },
					700: { value: "#124E87" },
					800: { value: "#124E87" },
					900: { value: "#124E87" },
				},
				accent: {
					50: { value: "#EAF6EF" },
					100: { value: "#D4EFE0" },
					200: { value: "#B8E4CA" },
					300: { value: "#8ED4A8" },
					400: { value: "#61BE81" },
					500: { value: "#3EAA5B" },
					600: { value: "#35924D" },
					700: { value: "#2C7D42" },
					800: { value: "#2C7D42" },
					900: { value: "#2C7D42" },
				},
				ink: {
					50: { value: "#F9FAFB" },
					100: { value: "#F3F4F6" },
					200: { value: "#E5E7EB" },
					300: { value: "#D1D5DB" },
					400: { value: "#9CA3AF" },
					500: { value: "#6B7280" },
					600: { value: "#4B5563" },
					700: { value: "#374151" },
					800: { value: "#1F2937" },
					900: { value: "#111827" },
				},
			},
			fonts: {
				heading: { value: "'DM Sans', system-ui, sans-serif" },
				body: { value: "'DM Sans', system-ui, sans-serif" },
				mono: { value: "'JetBrains Mono', ui-monospace, monospace" },
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
					canvas: {
						value: {
							base: "{colors.surface.canvas}",
							_dark: "#0B1220",
						},
					},
					panel: {
						value: {
							base: "{colors.surface.panel}",
							_dark: "#131B2B",
						},
					},
					muted: {
						value: {
							base: "{colors.surface.muted}",
							_dark: "#1A2538",
						},
					},
					hero: {
						value: {
							base: "{colors.laBlue.700}",
							_dark: "#103350",
						},
					},
					info: {
						value: {
							base: "{colors.surface.info}",
							_dark: "#18314B",
						},
					},
					success: {
						value: {
							base: "{colors.surface.success}",
							_dark: "#193325",
						},
					},
				},
				text: {
					primary: {
						value: {
							base: "{colors.laGray.900}",
							_dark: "#E6EEF8",
						},
					},
					secondary: {
						value: {
							base: "{colors.laGray.700}",
							_dark: "#B7C3D2",
						},
					},
					muted: {
						value: {
							base: "{colors.laGray.600}",
							_dark: "#93A2B7",
						},
					},
					inverse: {
						value: {
							base: "#FFFFFF",
							_dark: "#0B1220",
						},
					},
				},
				border: {
					default: {
						value: {
							base: "{colors.laGray.300}",
							_dark: "#2A374B",
						},
					},
					subtle: {
						value: {
							base: "{colors.laGray.200}",
							_dark: "#202C3D",
						},
					},
				},
				brand: {
					solid: {
						value: {
							base: "{colors.laBlue.500}",
							_dark: "{colors.laBlue.400}",
						},
					},
					emphasized: {
						value: {
							base: "{colors.laBlue.700}",
							_dark: "{colors.laBlue.300}",
						},
					},
					muted: {
						value: {
							base: "{colors.laBlue.100}",
							_dark: "#17324D",
						},
					},
					focusRing: {
						value: {
							base: "{colors.laBlue.500}",
							_dark: "{colors.laBlue.300}",
						},
					},
				},
				accent: {
					solid: {
						value: {
							base: "{colors.laGreen.500}",
							_dark: "{colors.laGreen.400}",
						},
					},
					emphasized: {
						value: {
							base: "{colors.laGreen.700}",
							_dark: "{colors.laGreen.300}",
						},
					},
					muted: {
						value: {
							base: "{colors.laGreen.100}",
							_dark: "#193927",
						},
					},
				},
				state: {
					warning: {
						bg: {
							value: {
								base: "#FFF6E6",
								_dark: "#3D2D10",
							},
						},
						fg: {
							value: {
								base: "#9A4D00",
								_dark: "#FFD7A0",
							},
						},
						border: {
							value: {
								base: "#F2C27B",
								_dark: "#7A5620",
							},
						},
					},
					success: {
						bg: {
							value: {
								base: "#E9F7EF",
								_dark: "#1A3827",
							},
						},
						fg: {
							value: {
								base: "#256B39",
								_dark: "#A4F0BF",
							},
						},
						border: {
							value: {
								base: "#A9DDB9",
								_dark: "#2A5A3C",
							},
						},
					},
					danger: {
						bg: {
							value: {
								base: "#FFF0F0",
								_dark: "#3B1C23",
							},
						},
						fg: {
							value: {
								base: "#B53045",
								_dark: "#FFB8C5",
							},
						},
						border: {
							value: {
								base: "#F5B5C2",
								_dark: "#6A2F3B",
							},
						},
					},
				},
			},
		},
	},
});

export const appSystem = createSystem(defaultConfig, config);
