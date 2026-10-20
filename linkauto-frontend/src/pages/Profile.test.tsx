import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ChakraProvider } from "@chakra-ui/react";
import { MemoryRouter, Route, Routes, useLocation } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";

import Profile from "./Profile";
import { profileService } from "../services/profileService";
import { appSystem } from "../theme/system";
import type { SessionData, UserAccount } from "../types/session";

function CurrentPath() {
	return <output data-testid="path">{useLocation().pathname}</output>;
}

const profileTree = (user: UserAccount) => {
	const session: SessionData = { accessToken: "t", tokenType: "Bearer", user };
	return (
		<MemoryRouter initialEntries={["/profile"]}>
			<ChakraProvider value={appSystem}>
				<Routes>
					<Route
						path="*"
						element={
							<>
								<Profile
									session={session}
									token="t"
									onLogout={vi.fn()}
									onProfileUpdated={vi.fn()}
									onNavigateToSearch={vi.fn()}
									onNavigateToBookings={vi.fn()}
								/>
								<CurrentPath />
							</>
						}
					/>
				</Routes>
			</ChakraProvider>
		</MemoryRouter>
	);
};

const renderProfile = (user: UserAccount) => render(profileTree(user));

const renderProfileWithRerender = (user: UserAccount) => {
	const result = render(profileTree(user));
	return { rerender: (next: UserAccount) => result.rerender(profileTree(next)) };
};

const student = (slug?: string): UserAccount => ({
	id: "01a1-internal-uuid",
	email: "ana@test.com",
	roles: ["ALUNO"],
	is_active: true,
	student_profile: { full_name: "Ana Souza", ...(slug ? { slug } : {}) },
	instructor_profile: null,
	created_at: "2026-10-18T00:00:00Z",
	updated_at: "2026-10-18T00:00:00Z",
});

describe("Profile public profile link", () => {
	it("opens the public profile by slug, never by internal ID", async () => {
		const user = userEvent.setup();
		renderProfile(student("ana-souza-campinas-1a2b"));

		await user.click(screen.getByRole("button", { name: /ver perfil público/i }));

		expect(screen.getByTestId("path")).toHaveTextContent("/students/ana-souza-campinas-1a2b");
	});

	it("hides the link when the profile has no slug", () => {
		renderProfile(student());

		expect(screen.queryByRole("button", { name: /ver perfil público/i })).not.toBeInTheDocument();
		expect(
			screen.queryByRole("button", { name: /visualizar meu perfil público/i }),
		).not.toBeInTheDocument();
	});
});

describe("Profile menu", () => {
	it("only offers entries that lead somewhere", () => {
		renderProfile(instructor());

		for (const label of [/meus veículos/i, /notificações/i, /planos e assinaturas/i]) {
			expect(screen.queryByRole("button", { name: label })).not.toBeInTheDocument();
		}
		expect(screen.getByRole("button", { name: /segurança e senha/i })).toBeInTheDocument();
	});
});

const instructor = (overrides: Partial<NonNullable<UserAccount["instructor_profile"]>> = {}): UserAccount => ({
	id: "01a1-internal-uuid",
	email: "rafa@test.com",
	roles: ["INSTRUTOR"],
	is_active: true,
	student_profile: null,
	instructor_profile: {
		slug: "rafa-1a2b",
		full_name: "Rafael Lima",
		city: "Campinas",
		state: "SP",
		price_per_hour: 70.5,
		action_radius_km: 15,
		...overrides,
	},
	created_at: "2026-10-18T00:00:00Z",
	updated_at: "2026-10-18T00:00:00Z",
});

describe("Profile editing (#89)", () => {
	afterEach(() => {
		vi.restoreAllMocks();
	});

	it("formats the hourly price as currency", () => {
		renderProfile(instructor());

		expect(screen.getByText("R$ 70,50")).toBeInTheDocument();
	});

	it("drops unsaved changes on Cancel", async () => {
		const user = userEvent.setup();
		renderProfile(instructor());

		await user.click(screen.getByRole("button", { name: /editar perfil/i }));
		const name = screen.getByPlaceholderText("Nome Completo");
		await user.clear(name);
		await user.type(name, "Nome não salvo");
		await user.click(screen.getByRole("button", { name: /cancelar/i }));

		expect(screen.queryByText("Nome não salvo")).not.toBeInTheDocument();
		expect(screen.getAllByText("Rafael Lima").length).toBeGreaterThan(0);

		// Editing again starts from the stored profile, not the abandoned edit
		await user.click(screen.getByRole("button", { name: /editar perfil/i }));
		expect(screen.getByPlaceholderText("Nome Completo")).toHaveValue("Rafael Lima");
	});

	it("starts editing from the latest stored profile", async () => {
		const user = userEvent.setup();
		const { rerender } = renderProfileWithRerender(instructor());

		// The session was refreshed (e.g. /users/me) after the page first rendered
		rerender(instructor({ full_name: "Rafael Lima Souza" }));
		await user.click(screen.getByRole("button", { name: /editar perfil/i }));

		expect(screen.getByPlaceholderText("Nome Completo")).toHaveValue("Rafael Lima Souza");
	});

	it("lets users with both roles edit their student profile", async () => {
		const user = userEvent.setup();
		const both: UserAccount = {
			...instructor(),
			roles: ["ALUNO", "INSTRUTOR"],
			student_profile: { slug: "rafa-aluno-1", full_name: "Rafa Aluno", license_type: "B" },
		};
		const saveStudent = vi
			.spyOn(profileService, "updateStudentProfile")
			.mockResolvedValue(both);
		const saveInstructor = vi.spyOn(profileService, "updateInstructorProfile");
		renderProfile(both);

		await user.click(screen.getByRole("button", { name: "Perfil de aluno" }));
		await user.click(screen.getByRole("button", { name: /editar perfil/i }));
		expect(screen.getByPlaceholderText("Nome Completo")).toHaveValue("Rafa Aluno");
		await user.click(screen.getByRole("button", { name: /salvar/i }));

		await waitFor(() => {
			expect(saveStudent).toHaveBeenCalled();
		});
		expect(saveInstructor).not.toHaveBeenCalled();
	});
});
