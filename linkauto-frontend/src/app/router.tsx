import {
	useCallback,
	useEffect,
	useEffectEvent,
	useMemo,
	useState,
	type ReactNode,
} from "react";
import {
	BrowserRouter,
	Navigate,
	Route,
	Routes,
	useNavigate,
} from "react-router-dom";

import InstructorDashboard from "../pages/InstructorDashboard";
import Login from "../pages/Login";
import Profile from "../pages/Profile";
import { httpClient } from "../services/httpClient";
import { useSessionStore } from "../state/sessionStore";
import type {
	DashboardRequest,
	ProfileUserData,
	UiRole,
	UserAccount,
} from "../types/session";

interface RouteGuardProps {
	readonly children: ReactNode;
}

interface RoleRouteProps extends RouteGuardProps {
	readonly roles: string[];
}

const toUiRole = (roles: string[]): UiRole => {
	if (roles.includes("ADMIN")) {
		return "admin";
	}

	if (roles.includes("INSTRUTOR")) {
		return "instructor";
	}

	return "student";
};

function ProtectedRoute({ children }: RouteGuardProps) {
	const { isAuthenticated } = useSessionStore();
	if (!isAuthenticated) {
		return <Navigate to="/login" replace />;
	}

	return children;
}

function RoleRoute({ roles, children }: RoleRouteProps) {
	const { roles: userRoles } = useSessionStore();
	const allowed = roles.some((role) => userRoles.includes(role));
	if (!allowed) {
		return <Navigate to="/profile" replace />;
	}

	return children;
}

function LoginRoute() {
	const navigate = useNavigate();
	const { signIn } = useSessionStore();

	const handleAuthenticate = async ({
		email,
		password,
	}: {
		email: string;
		password: string;
		preferredRole: "student" | "instructor";
	}) => {
		const session = await signIn({ email, password });
		if (session.user.roles.includes("ADMIN")) {
			navigate("/admin/instructors", { replace: true });
			return;
		}

		navigate("/profile", { replace: true });
	};

	return <Login onAuthenticate={handleAuthenticate} />;
}

function ProfileRoute() {
	const navigate = useNavigate();
	const { session, signOut } = useSessionStore();
	const [profile, setProfile] = useState<UserAccount | null>(
		session?.user ?? null,
	);

	const applyProfile = useEffectEvent((nextProfile: UserAccount) => {
		setProfile(nextProfile);
	});

	useEffect(() => {
		let active = true;

		const syncProfile = async () => {
			if (!session?.accessToken) {
				return;
			}

			const payload = await httpClient.get<UserAccount>("/users/me", {
				token: session.accessToken,
			});
			if (active) {
				applyProfile(payload.data);
			}
		};

		void syncProfile().catch(() => {
			if (active) {
				setProfile(session?.user ?? null);
			}
		});

		return () => {
			active = false;
		};
	}, [session?.accessToken, session?.user]);

	const role = toUiRole(profile?.roles ?? []);
	const userData: ProfileUserData = {
		name:
			profile?.student_profile?.full_name ||
			profile?.instructor_profile?.full_name ||
			"Conta LinkAuto",
		email: profile?.email || "usuario@linkauto.app",
		role,
	};

	return (
		<Profile
			userData={userData}
			onLogout={() => {
				signOut();
				navigate("/login", { replace: true });
			}}
			onNavigateToVehicles={() => navigate("/profile")}
		/>
	);
}

function AdminInstructorDashboardRoute() {
	const { session } = useSessionStore();
	const token = session?.accessToken;
	const [requests, setRequests] = useState<DashboardRequest[]>([]);

	const loadPending = useCallback(async (): Promise<DashboardRequest[]> => {
		if (!token) {
			return [];
		}

		const payload = await httpClient.get<UserAccount[]>(
			"/admin/instructors?status=PENDENTE",
			{
				token,
			},
		);

		const mapped = payload.data.map((item) => ({
			id: item.id,
			name: item.instructor_profile?.full_name || item.email,
			city: item.instructor_profile?.city || "Sem cidade",
			date: "Pendente",
			time: "--",
		}));
		return mapped;
	}, [token]);

	useEffect(() => {
		let active = true;

		void loadPending()
			.then((nextRequests) => {
				if (active) {
					setRequests(nextRequests);
				}
			})
			.catch(() => {
				if (active) {
					setRequests([]);
				}
			});

		return () => {
			active = false;
		};
	}, [loadPending]);

	const instructorData = useMemo(
		() => ({
			name: session?.user?.email || "Admin LinkAuto",
			rating: 5,
		}),
		[session?.user?.email],
	);

	const approve = async (instructorId: string) => {
		if (!token) {
			return;
		}

		await httpClient.patch<UserAccount>(
			`/admin/instructors/${instructorId}/approve`,
			{},
			{ token },
		);
		setRequests(await loadPending());
	};

	const reject = async (instructorId: string) => {
		if (!token) {
			return;
		}

		await httpClient.patch<UserAccount>(
			`/admin/instructors/${instructorId}/reject`,
			{ reason: "Rejeitado pela revisao administrativa." },
			{ token },
		);
		setRequests(await loadPending());
	};

	return (
		<InstructorDashboard
			instructorData={instructorData}
			requests={requests}
			onAccept={approve}
			onReject={reject}
			onViewStudents={() => undefined}
			dashboardTitle="Painel Administrativo"
			pendingLabel="Instrutores pendentes"
		/>
	);
}

function RootRedirect() {
	const { roles } = useSessionStore();
	if (roles.includes("ADMIN")) {
		return <Navigate to="/admin/instructors" replace />;
	}

	return <Navigate to="/profile" replace />;
}

export default function AppRouter() {
	return (
		<BrowserRouter>
			<Routes>
				<Route path="/login" element={<LoginRoute />} />
				<Route
					path="/profile"
					element={
						<ProtectedRoute>
							<ProfileRoute />
						</ProtectedRoute>
					}
				/>
				<Route
					path="/admin/instructors"
					element={
						<ProtectedRoute>
							<RoleRoute roles={["ADMIN"]}>
								<AdminInstructorDashboardRoute />
							</RoleRoute>
						</ProtectedRoute>
					}
				/>
				<Route
					path="/"
					element={
						<ProtectedRoute>
							<RootRedirect />
						</ProtectedRoute>
					}
				/>
				<Route path="*" element={<Navigate to="/" replace />} />
			</Routes>
		</BrowserRouter>
	);
}
