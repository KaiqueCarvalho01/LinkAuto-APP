import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ChakraProvider } from "@chakra-ui/react";
import { MemoryRouter, Route, Routes, useLocation } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { LoginRoute, ProtectedRoute } from "./router";
import { appSystem } from "../theme/system";

const session = vi.hoisted(() => ({
	isAuthenticated: false,
	roles: [] as string[],
}));

vi.mock("../state/sessionStore", () => ({
	useSessionStore: () => ({
		isAuthenticated: session.isAuthenticated,
		roles: session.roles,
		signIn: vi.fn(async () => {
			session.isAuthenticated = true;
			session.roles = ["ALUNO"];
			return { user: { roles: ["ALUNO"] } };
		}),
	}),
}));

function CurrentPage({ name }: { readonly name: string }) {
	const location = useLocation();
	const state = location.state as { instructor?: { slug: string } } | null;
	return (
		<p>
			{name} {location.search} {state?.instructor?.slug}
		</p>
	);
}

const renderAt = (entry: string | { pathname: string; state: unknown }) =>
	render(
		<ChakraProvider value={appSystem}>
			<MemoryRouter initialEntries={[entry]}>
				<Routes>
					<Route path="/login" element={<LoginRoute />} />
					<Route path="/search" element={<CurrentPage name="Busca" />} />
					<Route
						path="/my-lessons"
						element={
							<ProtectedRoute>
								<CurrentPage name="Minhas aulas" />
							</ProtectedRoute>
						}
					/>
				</Routes>
			</MemoryRouter>
		</ChakraProvider>,
	);

const logIn = async () => {
	const user = userEvent.setup();
	await user.type(screen.getByLabelText("E-mail"), "camila@linkauto.app");
	await user.type(screen.getByLabelText("Senha"), "SenhaForte123");
	await user.click(screen.getByRole("button", { name: "Entrar no LinkAuto" }));
};

describe("login redirects", () => {
	beforeEach(() => {
		session.isAuthenticated = false;
		session.roles = [];
	});

	it("returns to the protected page the visitor tried to open", async () => {
		renderAt("/my-lessons?status=PENDENTE");

		await logIn();

		expect(await screen.findByText(/Minhas aulas \?status=PENDENTE/)).toBeInTheDocument();
	});

	it("keeps the navigation state of the page it returns to", async () => {
		renderAt({
			pathname: "/login",
			state: { from: { pathname: "/my-lessons", state: { instructor: { slug: "marcos-lima" } } } },
		});

		await logIn();

		expect(await screen.findByText(/Minhas aulas\s+marcos-lima/)).toBeInTheDocument();
	});

	it("goes to the home page of the role when there is nowhere to return to", async () => {
		renderAt("/login");

		await logIn();

		expect(await screen.findByText(/Busca/)).toBeInTheDocument();
	});

	it("sends an already signed-in visitor straight to the page they came from", async () => {
		session.isAuthenticated = true;
		session.roles = ["ALUNO"];
		renderAt({ pathname: "/login", state: { from: { pathname: "/my-lessons" } } });

		expect(await screen.findByText(/Minhas aulas/)).toBeInTheDocument();
	});
});
