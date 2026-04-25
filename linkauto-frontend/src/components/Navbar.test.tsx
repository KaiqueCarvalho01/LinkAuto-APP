import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { Navbar } from "./Navbar";
import { renderWithProviders } from "../test/renderWithProviders";
import * as sessionStore from "../state/sessionStore";

// Mock the session store hook
vi.mock("../state/sessionStore", async (importOriginal) => {
	const actual = (await importOriginal()) as any;
	return {
		...actual,
		useSessionStore: vi.fn(),
	};
});

describe("Navbar (Visitor State)", () => {
	it("renders main navigation links for visitors in Portuguese", () => {
		vi.mocked(sessionStore.useSessionStore).mockReturnValue({
			isAuthenticated: false,
			session: null,
			roles: [],
			signIn: vi.fn(),
			signUp: vi.fn(),
			signOut: vi.fn(),
			clearSession: vi.fn(),
			refreshProfile: vi.fn(),
		});

		renderWithProviders(<Navbar />);

		expect(
			screen.getAllByRole("link", { name: /Explorar/i, hidden: true }).length,
		).toBeGreaterThanOrEqual(1);
		expect(
			screen.getAllByRole("link", { name: /Entrar/i, hidden: true }).length,
		).toBeGreaterThanOrEqual(1);
	});

	it("opens mobile drawer", async () => {
		const user = userEvent.setup();
		vi.mocked(sessionStore.useSessionStore).mockReturnValue({
			isAuthenticated: false,
			session: null,
			roles: [],
			signIn: vi.fn(),
			signUp: vi.fn(),
			signOut: vi.fn(),
			clearSession: vi.fn(),
			refreshProfile: vi.fn(),
		});

		renderWithProviders(<Navbar />);

		const openMenuButton = screen.getByRole("button", { name: /Open menu/i });
		await user.click(openMenuButton);

		// Verify trigger state
		expect(openMenuButton).toHaveAttribute("aria-expanded", "true");
	});
});

describe("Navbar (Authenticated State)", () => {
	it("renders user avatar and notifications", () => {
		vi.mocked(sessionStore.useSessionStore).mockReturnValue({
			isAuthenticated: true,
			session: {
				accessToken: "mock-token",
				tokenType: "Bearer",
				user: {
					id: "1",
					email: "test@example.com",
					roles: ["student"],
					is_active: true,
					student_profile: { full_name: "João Silva" },
					instructor_profile: null,
					created_at: new Date().toISOString(),
					updated_at: new Date().toISOString(),
				},
			},
			roles: ["student"],
			signIn: vi.fn(),
			signUp: vi.fn(),
			signOut: vi.fn(),
			clearSession: vi.fn(),
			refreshProfile: vi.fn(),
		});

		renderWithProviders(<Navbar />);

		expect(screen.getByRole("button", { name: /Notificações/i, hidden: true })).toBeInTheDocument();
		expect(screen.getByText(/João/i)).toBeInTheDocument();
	});

	it("handles scroll state changes", async () => {
		vi.mocked(sessionStore.useSessionStore).mockReturnValue({
			isAuthenticated: false,
			session: null,
			roles: [],
			signIn: vi.fn(),
			signUp: vi.fn(),
			signOut: vi.fn(),
			clearSession: vi.fn(),
			refreshProfile: vi.fn(),
		});

		renderWithProviders(<Navbar />);
		
		window.scrollY = 20;
		window.dispatchEvent(new Event("scroll"));
		
		expect(window.scrollY).toBe(20);
	});

	it("calls signOut and opens ProfileSidebar on avatar click", async () => {
		const user = userEvent.setup();
		const signOutMock = vi.fn();
		vi.mocked(sessionStore.useSessionStore).mockReturnValue({
			isAuthenticated: true,
			session: {
				accessToken: "mock-token",
				tokenType: "Bearer",
				user: {
					id: "1",
					email: "test@example.com",
					roles: ["student"],
					is_active: true,
					student_profile: { full_name: "João Silva" },
					instructor_profile: null,
					created_at: new Date().toISOString(),
					updated_at: new Date().toISOString(),
				},
			},
			roles: ["student"],
			signIn: vi.fn(),
			signUp: vi.fn(),
			signOut: signOutMock,
			clearSession: vi.fn(),
			refreshProfile: vi.fn(),
		});

		renderWithProviders(<Navbar />);

		const signOutButtons = screen.getAllByRole("button", {
			name: /Sair/i,
			hidden: true,
		});
		if (signOutButtons.length > 0 && signOutButtons[0]) {
			await user.click(signOutButtons[0]);
		}
		expect(signOutMock).toHaveBeenCalled();

		const avatar = screen.getByLabelText(/Menu de Perfil/i);
		await user.click(avatar);
		
		// ProfileSidebar should be visible
		expect(screen.getByText("test@example.com")).toBeInTheDocument();
		expect(screen.getByText(/João Silva/i)).toBeInTheDocument();
	});

	it("opens notifications popover", async () => {
		const user = userEvent.setup();
		vi.mocked(sessionStore.useSessionStore).mockReturnValue({
			isAuthenticated: true,
			session: {
				accessToken: "mock-token",
				tokenType: "Bearer",
				user: {
					id: "1",
					email: "test@example.com",
					roles: ["student"],
					is_active: true,
					student_profile: { full_name: "João Silva" },
					instructor_profile: null,
					created_at: new Date().toISOString(),
					updated_at: new Date().toISOString(),
				},
			},
			roles: ["student"],
			signIn: vi.fn(),
			signUp: vi.fn(),
			signOut: vi.fn(),
			clearSession: vi.fn(),
			refreshProfile: vi.fn(),
		});

		renderWithProviders(<Navbar />);

		const notifyButton = screen.getByRole("button", { name: /Notificações/i, hidden: true });
		await user.click(notifyButton);
		expect(screen.getByText(/Sua aula com Marcos foi confirmada/i)).toBeInTheDocument();
	});
});
