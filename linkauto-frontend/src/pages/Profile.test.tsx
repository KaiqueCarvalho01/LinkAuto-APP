import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ChakraProvider } from "@chakra-ui/react";
import { MemoryRouter, Route, Routes, useLocation } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";

import Profile from "./Profile";
import { appSystem } from "../theme/system";
import type { SessionData, UserAccount } from "../types/session";

function CurrentPath() {
	return <output data-testid="path">{useLocation().pathname}</output>;
}

const renderProfile = (user: UserAccount) => {
	const session: SessionData = { accessToken: "t", tokenType: "Bearer", user };
	render(
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
									onNavigateToVehicles={vi.fn()}
								/>
								<CurrentPath />
							</>
						}
					/>
				</Routes>
			</ChakraProvider>
		</MemoryRouter>,
	);
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
	});
});
