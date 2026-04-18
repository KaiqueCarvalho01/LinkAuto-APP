import React, { useCallback, useEffect, useMemo, useState } from "react";
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

const toUiRole = (roles) => {
	if (roles.includes("ADMIN")) return "admin";
	if (roles.includes("INSTRUTOR")) return "instructor";
	return "student";
};

function ProtectedRoute({ children }) {
	const { isAuthenticated } = useSessionStore();
	if (!isAuthenticated) {
		return <Navigate to="/login" replace />;
	}
	return children;
}

function RoleRoute({ roles, children }) {
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

	const handleAuthenticate = async ({ email, password }) => {
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
	const [profile, setProfile] = useState(session?.user ?? null);

	useEffect(() => {
		let active = true;
		const syncProfile = async () => {
			if (!session?.accessToken) return;
			const payload = await httpClient.get("/users/me", {
				token: session.accessToken,
			});
			if (active) setProfile(payload.data);
		};
		syncProfile().catch(() => {
			if (active) setProfile(session?.user ?? null);
		});
		return () => {
			active = false;
		};
	}, [session?.accessToken, session?.user]);

	const role = toUiRole(profile?.roles ?? []);
	const userData = {
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
	const [requests, setRequests] = useState([]);

	const loadPending = useCallback(async () => {
		if (!token) {
			setRequests([]);
			return;
		}
		const payload = await httpClient.get(
			"/admin/instructors?status=PENDENTE",
			{ token },
		);
		const mapped = payload.data.map((item) => ({
			id: item.id,
			name: item.instructor_profile?.full_name || item.email,
			city: item.instructor_profile?.city || "Sem cidade",
			date: "Pendente",
			time: "--",
		}));
		setRequests(mapped);
	}, [token]);

	useEffect(() => {
		const timer = setTimeout(() => {
			loadPending().catch(() => {
				setRequests([]);
			});
		}, 0);
		return () => {
			clearTimeout(timer);
		};
	}, [loadPending]);

	const instructorData = useMemo(
		() => ({
			name: session?.user?.email || "Admin",
			rating: 5.0,
		}),
		[session?.user?.email],
	);

	const approve = async (instructorId) => {
		await httpClient.patch(
			`/admin/instructors/${instructorId}/approve`,
			{},
			{ token },
		);
		await loadPending();
	};

	const reject = async (instructorId) => {
		await httpClient.patch(
			`/admin/instructors/${instructorId}/reject`,
			{ reason: "Rejeitado pela revisão administrativa." },
			{ token },
		);
		await loadPending();
	};

	return (
		<InstructorDashboard
			instructorData={instructorData}
			requests={requests}
			onAccept={approve}
			onReject={reject}
			onViewStudents={() => {}}
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
