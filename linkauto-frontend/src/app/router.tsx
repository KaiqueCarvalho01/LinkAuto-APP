import {
	useCallback,
	useEffect,
	useEffectEvent,
	useMemo,
	useState,
	type ReactNode,
} from "react";
import { MoonStar, SunMedium } from "lucide-react";
import { Box, IconButton } from "@chakra-ui/react";
import {
	BrowserRouter,
	Navigate,
	Route,
	Routes,
	useLocation,
	useNavigate,
} from "react-router-dom";

import Home from "../pages/Home";
import InstructorDashboard from "../pages/InstructorDashboard";
import LessonDetails from "../pages/LessonDetails";
import Login from "../pages/Login";
import MyLessons from "../pages/MyLessons";
import Profile from "../pages/Profile";
import SearchPage from "../pages/SearchPage";
import Register from "../pages/Register";
import About from "../pages/About";
import Contact from "../pages/Contact";
import Notifications from "../pages/Notifications";
import Help from "../pages/Help";
import AuditLog from "../pages/admin/AuditLog";
import FirstLicense from "../pages/students/FirstLicense";
import LicensedDrivers from "../pages/students/LicensedDrivers";
import HowItWorksStudent from "../pages/students/HowItWorks";
import HowItWorksInstructor from "../pages/instructors/HowItWorks";
import Benefits from "../pages/instructors/Benefits";
import Simulator from "../pages/instructors/Simulator";
import { httpClient } from "../services/httpClient";
import { useSessionStore } from "../state/sessionStore";
import type { InstructorSummary } from "../types/instructor";
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

type ThemeMode = "light" | "dark";

const COLOR_MODE_STORAGE_KEY = "linkauto-color-mode";

const resolvePreferredColorMode = (): ThemeMode => {
	if (globalThis.window === undefined) {
		return "light";
	}

	const stored = globalThis.localStorage.getItem(COLOR_MODE_STORAGE_KEY);
	if (stored === "dark" || stored === "light") {
		return stored;
	}

	return globalThis.matchMedia("(prefers-color-scheme: dark)").matches
		? "dark"
		: "light";
};

const applyColorMode = (mode: ThemeMode) => {
	if (typeof document === "undefined") {
		return;
	}

	const root = document.documentElement;
	root.classList.toggle("dark", mode === "dark");
	root.style.colorScheme = mode;
};

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
		return <Navigate to="/buscar" replace />;
	}

	return children;
}

function HomeRoute() {
	const navigate = useNavigate();
	const { isAuthenticated } = useSessionStore();

	return (
		<Home
			isAuthenticated={isAuthenticated}
			onOpenLogin={() => navigate("/login")}
			onOpenSearch={() => {
				if (isAuthenticated) {
					navigate("/buscar");
					return;
				}
				navigate("/login");
			}}
		/>
	);
}

function LoginRoute() {
	const navigate = useNavigate();
	const { isAuthenticated, roles, signIn } = useSessionStore();

	if (isAuthenticated) {
		if (roles.includes("ADMIN")) {
			return <Navigate to="/admin/instructors" replace />;
		}

		return <Navigate to="/buscar" replace />;
	}

	const handleAuthenticate = async ({
		email,
		password,
		preferredRole,
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

		if (
			preferredRole === "student" &&
			session.user.roles.includes("ALUNO")
		) {
			navigate("/buscar", { replace: true });
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
			onNavigateToSearch={() => navigate("/buscar")}
			onNavigateToBookings={() => navigate("/agendamentos")}
			onNavigateToVehicles={() => navigate("/profile")}
		/>
	);
}

function SearchRoute() {
	const navigate = useNavigate();
	const { session } = useSessionStore();

	return (
		<SearchPage
			token={session?.accessToken}
			onOpenProfile={() => navigate("/profile")}
			onStartBooking={(instructor) =>
				navigate("/bookings/new", { state: { instructor } })
			}
		/>
	);
}

function BookingDetailsRoute() {
	const navigate = useNavigate();
	const location = useLocation();
	const state = location.state as { instructor?: InstructorSummary } | null;

	return (
		<LessonDetails
			instructor={state?.instructor}
			onBack={() => navigate("/buscar")}
			onBookingCreated={() => {
				navigate("/agendamentos", { replace: true });
			}}
		/>
	);
}

function MyLessonsRoute() {
	const navigate = useNavigate();

	return <MyLessons onNewBooking={() => navigate("/buscar")} />;
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
	const { isAuthenticated, roles } = useSessionStore();
	if (!isAuthenticated) {
		return <Navigate to="/" replace />;
	}

	if (roles.includes("ADMIN")) {
		return <Navigate to="/admin/instructors" replace />;
	}

	return <Navigate to="/buscar" replace />;
}

function ColorModeToggle() {
	const [mode, setMode] = useState<ThemeMode>(() =>
		resolvePreferredColorMode(),
	);

	useEffect(() => {
		applyColorMode(mode);
		globalThis.localStorage.setItem(COLOR_MODE_STORAGE_KEY, mode);
	}, [mode]);

	const isDark = mode === "dark";

	return (
		<Box
			position="fixed"
			right={{ base: 4, md: 6 }}
			bottom={{ base: 4, md: 6 }}
			zIndex={60}>
			<IconButton
				aria-label={isDark ? "Ativar tema claro" : "Ativar tema escuro"}
				title={isDark ? "Ativar tema claro" : "Ativar tema escuro"}
				onClick={() => {
					setMode((current) =>
						current === "dark" ? "light" : "dark",
					);
				}}
				size="md"
				variant="ghost"
				border="1px solid"
				borderColor="border.default"
				bg="surface.panel"
				color="text.primary"
				boxShadow={{
					base: "0 12px 24px rgba(15, 42, 67, 0.16)",
					_dark: "0 12px 24px rgba(2, 6, 14, 0.44)",
				}}
				_hover={{ bg: "surface.muted" }}>
				{isDark ? <SunMedium size={16} /> : <MoonStar size={16} />}
			</IconButton>
		</Box>
	);
}

export default function AppRouter() {
	return (
		<BrowserRouter>
			<Routes>
				<Route path="/" element={<HomeRoute />} />
				<Route path="/login" element={<LoginRoute />} />
				<Route path="/register" element={<Register />} />
				<Route path="/about" element={<About />} />
				<Route path="/contact" element={<Contact />} />
				<Route path="/help" element={<Help />} />
				<Route
					path="/students/first-license"
					element={<FirstLicense />}
				/>
				<Route
					path="/students/licensed"
					element={<LicensedDrivers />}
				/>
				<Route
					path="/students/how-it-works"
					element={<HowItWorksStudent />}
				/>
				<Route
					path="/instructors/how-it-works"
					element={<HowItWorksInstructor />}
				/>
				<Route path="/instructors/benefits" element={<Benefits />} />
				<Route path="/instructors/simulator" element={<Simulator />} />
				<Route
					path="/profile"
					element={
						<ProtectedRoute>
							<ProfileRoute />
						</ProtectedRoute>
					}
				/>
				<Route
					path="/buscar"
					element={
						<ProtectedRoute>
							<RoleRoute roles={["ALUNO", "INSTRUTOR", "ADMIN"]}>
								<SearchRoute />
							</RoleRoute>
						</ProtectedRoute>
					}
				/>
				<Route
					path="/bookings/new"
					element={
						<ProtectedRoute>
							<RoleRoute roles={["ALUNO", "ADMIN"]}>
								<BookingDetailsRoute />
							</RoleRoute>
						</ProtectedRoute>
					}
				/>
				<Route
					path="/agendamentos"
					element={
						<ProtectedRoute>
							<RoleRoute roles={["ALUNO", "INSTRUTOR", "ADMIN"]}>
								<MyLessonsRoute />
							</RoleRoute>
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
					path="/notifications"
					element={
						<ProtectedRoute>
							<Notifications />
						</ProtectedRoute>
					}
				/>
				<Route
					path="/admin/audit"
					element={
						<ProtectedRoute>
							<RoleRoute roles={["ADMIN"]}>
								<AuditLog />
							</RoleRoute>
						</ProtectedRoute>
					}
				/>
				<Route path="/app" element={<RootRedirect />} />
				<Route path="*" element={<RootRedirect />} />
			</Routes>
			<ColorModeToggle />
		</BrowserRouter>
	);
}
