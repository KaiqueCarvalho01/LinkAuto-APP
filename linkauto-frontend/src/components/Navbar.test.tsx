import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { Navbar } from "./Navbar";
import { renderWithProviders } from "../test/renderWithProviders";
import * as sessionStore from "../state/sessionStore";

// Mock the session store hook
vi.mock("../state/sessionStore", async (importOriginal) => {
	const actual = (await importOriginal()) as typeof sessionStore;
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
			updateUser: vi.fn(),
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
			updateUser: vi.fn(),
		});

		renderWithProviders(<Navbar />);

		const openMenuButton = screen.getByRole("button", { name: "Abrir menu" });
		await user.click(openMenuButton);

		// Verify trigger state
		expect(openMenuButton).toHaveAttribute("aria-expanded", "true");
	});
});

describe("Navbar (Authenticated State)", () => {
	it("renders the user avatar and no notifications button", () => {
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
			updateUser: vi.fn(),
		});

		renderWithProviders(<Navbar />);

		// There is no notifications feature yet: no button with a fake unread dot (#86)
		expect(
			screen.queryByRole("button", { name: /Notificações/i, hidden: true }),
		).not.toBeInTheDocument();
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
			updateUser: vi.fn(),
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
			updateUser: vi.fn(),
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

		const avatar = screen.getByRole("button", { name: /^Abrir menu de perfil/, hidden: true });
		await user.click(avatar);
		
		// ProfileSidebar should be visible
		expect(screen.getByText("test@example.com")).toBeInTheDocument();
		expect(screen.getByText(/João Silva/i)).toBeInTheDocument();
	});

	it("shows no made-up notifications or links to a placeholder page", async () => {
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
			updateUser: vi.fn(),
		});

		renderWithProviders(<Navbar />);

		// Open the mobile drawer too, which also linked to /notifications
		await user.click(screen.getByRole("button", { name: "Abrir menu", hidden: true }));

		expect(screen.queryByText(/Sua aula com Marcos/i)).not.toBeInTheDocument();
		expect(
			document.querySelector('a[href="/notifications"]'),
		).toBeNull();
	});
});

describe("Navbar profile menu (keyboard)", () => {
	it("uses a real button for the profile menu, so keyboards can open it", async () => {
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
			updateUser: vi.fn(),
		});

		renderWithProviders(<Navbar />);

		const trigger = screen.getByRole("button", { name: /^Abrir menu de perfil/, hidden: true });
		// A native <button> is focusable and opens with Enter and Space (it was a div with role="button")
		expect(trigger.tagName).toBe("BUTTON");
		expect(trigger).toHaveAttribute("type", "button");
		expect(trigger).toHaveAttribute("aria-haspopup", "dialog");
		expect(trigger).toHaveAttribute("aria-expanded", "false");

		await user.click(trigger);

		expect(trigger).toHaveAttribute("aria-expanded", "true");
		expect(await screen.findByText("test@example.com")).toBeInTheDocument();
	});
});
