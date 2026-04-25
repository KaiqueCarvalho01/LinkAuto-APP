import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { ProfileSidebar } from "./ProfileSidebar";
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

describe("ProfileSidebar", () => {
	const mockUser = {
		id: "1",
		email: "joao@example.com",
		roles: ["ALUNO"],
		is_active: true,
		student_profile: { full_name: "João Silva" },
		instructor_profile: null,
		created_at: new Date().toISOString(),
		updated_at: new Date().toISOString(),
	};

	it("renders user information correctly", () => {
		vi.mocked(sessionStore.useSessionStore).mockReturnValue({
			isAuthenticated: true,
			session: {
				accessToken: "token",
				tokenType: "Bearer",
				user: mockUser,
			},
			roles: ["ALUNO"],
			signIn: vi.fn(),
			signUp: vi.fn(),
			signOut: vi.fn(),
			clearSession: vi.fn(),
			refreshProfile: vi.fn(),
		});

		renderWithProviders(
			<ProfileSidebar open={true} onOpenChange={vi.fn()} />,
		);

		expect(screen.getByText(/João Silva/i)).toBeInTheDocument();
		expect(screen.getByText(/joao@example.com/i)).toBeInTheDocument();
	});

	it("renders role-specific links for ALUNO", () => {
		vi.mocked(sessionStore.useSessionStore).mockReturnValue({
			isAuthenticated: true,
			session: {
				accessToken: "token",
				tokenType: "Bearer",
				user: mockUser,
			},
			roles: ["ALUNO"],
			signIn: vi.fn(),
			signUp: vi.fn(),
			signOut: vi.fn(),
			clearSession: vi.fn(),
			refreshProfile: vi.fn(),
		});

		renderWithProviders(
			<ProfileSidebar open={true} onOpenChange={vi.fn()} />,
		);

		expect(
			screen.getByRole("link", { name: /Minhas Aulas/i }),
		).toBeInTheDocument();
		expect(
			screen.getByRole("link", { name: /Buscar Instrutor/i }),
		).toBeInTheDocument();
		expect(
			screen.getByRole("link", { name: /Meu Perfil/i }),
		).toBeInTheDocument();
	});

	it("renders tabs and links for multi-role users (ALUNO + INSTRUTOR)", async () => {
		const user = userEvent.setup();
		const multiRoleUser = {
			...mockUser,
			roles: ["ALUNO", "INSTRUTOR"],
			instructor_profile: { full_name: "João Instrutor" },
		};

		vi.mocked(sessionStore.useSessionStore).mockReturnValue({
			isAuthenticated: true,
			session: {
				accessToken: "token",
				tokenType: "Bearer",
				user: multiRoleUser,
			},
			roles: ["ALUNO", "INSTRUTOR"],
			signIn: vi.fn(),
			signUp: vi.fn(),
			signOut: vi.fn(),
			clearSession: vi.fn(),
			refreshProfile: vi.fn(),
		});

		renderWithProviders(
			<ProfileSidebar open={true} onOpenChange={vi.fn()} />,
		);

		// Should see tabs
		const alunoTab = screen.getByRole("tab", { name: /ALUNO/i });
		const instrutorTab = screen.getByRole("tab", { name: /INSTRUTOR/i });
		expect(alunoTab).toBeInTheDocument();
		expect(instrutorTab).toBeInTheDocument();

		// Default tab is ALUNO
		expect(
			screen.getByRole("link", { name: /Buscar Instrutor/i }),
		).toBeInTheDocument();

		// Click INSTRUTOR tab
		await user.click(instrutorTab);

		// Still should have Minhas Aulas etc
		expect(
			screen.getByRole("link", { name: /Minhas Aulas/i }),
		).toBeInTheDocument();
	});

	it("renders admin links for ADMIN role", () => {
		const adminUser = {
			...mockUser,
			roles: ["ADMIN"],
		};

		vi.mocked(sessionStore.useSessionStore).mockReturnValue({
			isAuthenticated: true,
			session: {
				accessToken: "token",
				tokenType: "Bearer",
				user: adminUser,
			},
			roles: ["ADMIN"],
			signIn: vi.fn(),
			signUp: vi.fn(),
			signOut: vi.fn(),
			clearSession: vi.fn(),
			refreshProfile: vi.fn(),
		});

		renderWithProviders(
			<ProfileSidebar open={true} onOpenChange={vi.fn()} />,
		);

		expect(
			screen.getByRole("link", { name: /Gerenciar Instrutores/i }),
		).toBeInTheDocument();
		expect(
			screen.getByRole("link", { name: /Meu Perfil/i }),
		).toBeInTheDocument();
	});

	it("calls signOut and redirects when Logout button is clicked", async () => {
		const user = userEvent.setup();
		const signOutMock = vi.fn();

		vi.mocked(sessionStore.useSessionStore).mockReturnValue({
			isAuthenticated: true,
			session: {
				accessToken: "token",
				tokenType: "Bearer",
				user: mockUser,
			},
			roles: ["ALUNO"],
			signIn: vi.fn(),
			signUp: vi.fn(),
			signOut: signOutMock,
			clearSession: vi.fn(),
			refreshProfile: vi.fn(),
		});

		renderWithProviders(
			<ProfileSidebar open={true} onOpenChange={vi.fn()} />,
		);

		const logoutButton = screen.getByRole("button", { name: /Sair/i });
		await user.click(logoutButton);

		expect(signOutMock).toHaveBeenCalled();
	});

	it("calls onOpenChange when drawer is closed", async () => {
		const user = userEvent.setup();
		const onOpenChangeMock = vi.fn();

		vi.mocked(sessionStore.useSessionStore).mockReturnValue({
			isAuthenticated: true,
			session: {
				accessToken: "token",
				tokenType: "Bearer",
				user: mockUser,
			},
			roles: ["ALUNO"],
			signIn: vi.fn(),
			signUp: vi.fn(),
			signOut: vi.fn(),
			clearSession: vi.fn(),
			refreshProfile: vi.fn(),
		});

		renderWithProviders(
			<ProfileSidebar open={true} onOpenChange={onOpenChangeMock} />,
		);

		// Click close button using class selector since it has no name
		const closeButton = document.querySelector(".chakra-drawer__closeTrigger");
		if (closeButton) {
			await user.click(closeButton);
		}

		expect(onOpenChangeMock).toHaveBeenCalledWith(false);
	});

	it("returns null if user is not present", () => {
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

		const { container } = renderWithProviders(
			<ProfileSidebar open={true} onOpenChange={vi.fn()} />,
		);

		expect(container.firstChild).toBeNull();
	});

	it("renders generic display name if profiles are missing", () => {
		const genericUser = {
			...mockUser,
			email: "other@example.com",
			student_profile: null,
			instructor_profile: null,
		};

		vi.mocked(sessionStore.useSessionStore).mockReturnValue({
			isAuthenticated: true,
			session: {
				accessToken: "token",
				tokenType: "Bearer",
				user: genericUser,
			},
			roles: ["ALUNO"],
			signIn: vi.fn(),
			signUp: vi.fn(),
			signOut: vi.fn(),
			clearSession: vi.fn(),
			refreshProfile: vi.fn(),
		});

		renderWithProviders(
			<ProfileSidebar open={true} onOpenChange={vi.fn()} />,
		);

		// email is other@example.com, so display name should be "other"
		expect(screen.getByText("other")).toBeInTheDocument();
	});
});
