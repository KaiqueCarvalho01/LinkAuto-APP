import {
	useCallback,
	useEffect,
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
	useParams,
	useSearchParams,
	Outlet,
} from "react-router-dom";

import { Navbar } from "../components/Navbar";
import { Footer } from "../components/Footer";
import { InstructorAgenda } from "../components/InstructorAgenda";
import { InstructorUpcomingLessons } from "../components/InstructorUpcomingLessons";

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
import Help from "../pages/Help";
import Terms from "../pages/Terms";
import Privacy from "../pages/Privacy";
import PasswordReset from "../pages/PasswordReset";
import PasswordResetConfirm from "../pages/PasswordResetConfirm";
import FirstLicense from "../pages/students/FirstLicense";
import LicensedDrivers from "../pages/students/LicensedDrivers";
import HowItWorksStudent from "../pages/students/HowItWorks";
import HowItWorksInstructor from "../pages/instructors/HowItWorks";
import Benefits from "../pages/instructors/Benefits";
import Simulator from "../pages/instructors/Simulator";
import InstructorPublicProfilePage from "../pages/InstructorPublicProfilePage";
import StudentPublicProfilePage from "../pages/StudentPublicProfilePage";
import { adminService, type PendingInstructors } from "../services/adminService";
import { bookingService } from "../services/bookingService";
import { httpClient } from "../services/httpClient";
import { useSessionStore } from "../state/sessionStore";
import { homePathFor } from "./homePath";
import { returnToFrom } from "./returnTo";
import type {
	AdminStats,
	DashboardRequest,
	InstructorStats,
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



export function ProtectedRoute({ children }: RouteGuardProps) {
	const location = useLocation();
	const { isAuthenticated } = useSessionStore();
	if (!isAuthenticated) {
		return <Navigate to="/login" replace state={{ from: location }} />;
	}

	return children;
}

function RoleRoute({ roles, children }: RoleRouteProps) {
	const { roles: userRoles } = useSessionStore();
	const allowed = roles.some((role) => userRoles.includes(role));
	if (!allowed) {
		return <Navigate to="/search" replace />;
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
					navigate("/search");
					return;
				}
				navigate("/login");
			}}
		/>
	);
}

export function LoginRoute() {
	const navigate = useNavigate();
	const location = useLocation();
	const { isAuthenticated, roles, signIn } = useSessionStore();
	const returnTo = returnToFrom(location.state);

	if (isAuthenticated) {
		return returnTo ? (
			<Navigate to={returnTo.path} state={returnTo.state} replace />
		) : (
			<Navigate to={homePathFor(roles)} replace />
		);
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
		if (returnTo) {
			navigate(returnTo.path, { replace: true, state: returnTo.state });
			return;
		}
		navigate(homePathFor(session.user.roles, preferredRole), { replace: true });
	};

	return <Login onAuthenticate={handleAuthenticate} />;
}

function RegisterRoute() {
	const navigate = useNavigate();
	const [searchParams] = useSearchParams();
	const { signUp, isAuthenticated } = useSessionStore();
	const initialRole = searchParams.get("role") === "instructor" ? "instructor" : "student";

	if (isAuthenticated) {
		return <Navigate to="/search" replace />;
	}

	const handleRegister = async ({
		name,
		email,
		password,
		preferredRole,
	}: {
		name: string;
		email: string;
		password: string;
		preferredRole: "student" | "instructor";
	}) => {
		const roles = preferredRole === "student" ? ["ALUNO"] : ["INSTRUTOR"];
		await signUp({ email, password, roles, fullName: name });
		// After successful registration, redirect to login
		navigate("/login", { replace: true });
	};

	return <Register onRegister={handleRegister} initialRole={initialRole} />;
}

function ProfileRoute() {
	const navigate = useNavigate();
	const { session, signOut, updateUser } = useSessionStore();
	const accessToken = session?.accessToken;

	// Refresh the signed-in user once per visit; the session (navbar, sidebar, dashboard
	// and the stored copy) is the single source of truth for the profile
	useEffect(() => {
		let active = true;
		if (!accessToken) return;
		httpClient
			.get<UserAccount>("/users/me", { token: accessToken })
			.then((payload) => {
				if (active) updateUser(payload.data);
			})
			.catch((err) => {
				console.error("Failed to refresh the profile:", err);
			});
		return () => {
			active = false;
		};
	}, [accessToken, updateUser]);

	return (
		<Profile
			session={session}
			token={accessToken}
			onLogout={() => {
				void signOut();
				navigate("/login", { replace: true });
			}}
			onProfileUpdated={updateUser}
			onNavigateToSearch={() => navigate("/search")}
			onNavigateToBookings={() => navigate("/my-lessons")}
		/>
	);
}

function SearchRoute() {
	const navigate = useNavigate();
	const { session } = useSessionStore();

	return (
		<SearchPage
			token={session?.accessToken}
			onOpenProfile={(instructor) => {
				if (instructor) {
					navigate(`/instructors/${instructor.slug || instructor.id}`);
				} else {
					navigate("/profile");
				}
			}}
			onStartBooking={(instructor) =>
				navigate(`/bookings/new/${instructor.slug || instructor.id}`)
			}
		/>
	);
}

function BookingDetailsRoute() {
	const navigate = useNavigate();
	const { slug = "" } = useParams<{ slug: string }>();
	const { session } = useSessionStore();

	return (
		<LessonDetails
			key={slug}
			instructorSlug={slug}
			token={session?.accessToken}
			onBack={() => navigate("/search")}
			onBookingCreated={() => {
				navigate("/my-lessons", { replace: true });
			}}
		/>
	);
}

function MyLessonsRoute() {
	const navigate = useNavigate();
	const { session } = useSessionStore();

	return <MyLessons token={session?.accessToken} onNewBooking={() => navigate("/search")} />;
}

function AdminInstructorDashboardRoute() {
	const { session } = useSessionStore();
	const token = session?.accessToken;
	const [requests, setRequests] = useState<DashboardRequest[]>([]);
	const [adminStats, setAdminStats] = useState<AdminStats | undefined>();

	const [pendingTotal, setPendingTotal] = useState(0);
	const [actionError, setActionError] = useState<string | null>(null);

	const loadPending = useCallback(async (): Promise<PendingInstructors> => {
		if (!token) {
			return { requests: [], total: 0 };
		}
		return adminService.getPendingInstructors(token);
	}, [token]);

	const applyPending = useCallback((pending: PendingInstructors) => {
		setRequests(pending.requests);
		setPendingTotal(pending.total);
	}, []);

	const loadStats = useCallback(async (): Promise<AdminStats | undefined> => {
		if (!token) return undefined;
		try {
			const res = await httpClient.get<{
				total_instructors: number;
				pending_instructors: number;
				approved_instructors: number;
				rejected_instructors: number;
				total_students: number;
				total_bookings: number;
			}>("/admin/stats", { token });
			if (res.data) {
				return {
					totalInstructors: res.data.total_instructors,
					pendingInstructors: res.data.pending_instructors,
					approvedInstructors: res.data.approved_instructors,
					rejectedInstructors: res.data.rejected_instructors,
					totalStudents: res.data.total_students,
					totalBookings: res.data.total_bookings,
				};
			}
		} catch (err) {
			console.error("Failed to load admin stats:", err);
		}
		return undefined;
	}, [token]);

	useEffect(() => {
		let active = true;

		void loadPending()
			.then((pending) => {
				if (active) {
					applyPending(pending);
				}
			})
			.catch((err) => {
				console.error("Failed to load pending instructors:", err);
				if (active) {
					setActionError("Não foi possível carregar os instrutores pendentes.");
				}
			});

		void loadStats().then((data) => {
			if (active && data) {
				setAdminStats(data);
			}
		});

		return () => {
			active = false;
		};
	}, [loadPending, loadStats, applyPending]);

	const instructorData = useMemo(
		() => ({
			name: session?.user?.email || "Admin LinkAuto",
			rating: 5,
		}),
		[session?.user?.email],
	);

	const refresh = async () => {
		try {
			applyPending(await loadPending());
		} catch (err) {
			console.error("Failed to reload pending instructors:", err);
		}
		const updatedStats = await loadStats();
		if (updatedStats) setAdminStats(updatedStats);
	};

	// Failures are shown to the admin, and the list reloaded so it shows the truth
	const decide = async (decision: () => Promise<void>, failure: string) => {
		setActionError(null);
		try {
			await decision();
		} catch (err) {
			console.error(failure, err);
			setActionError(failure);
		}
		await refresh();
	};

	const approve = async (instructorId: string) => {
		if (!token) return;
		await decide(
			() => adminService.approveInstructor(instructorId, token),
			"Não foi possível aprovar o instrutor. Tente novamente.",
		);
	};

	const reject = async (instructorId: string, reason?: string) => {
		if (!token) return;
		await decide(
			() => adminService.rejectInstructor(instructorId, reason ?? "", token),
			"Não foi possível recusar o instrutor. Tente novamente.",
		);
	};

	const pendingCount = pendingTotal;

	return (
		<InstructorDashboard
			instructorData={instructorData}
			requests={requests}
			onAccept={approve}
			onReject={reject}
			dashboardTitle="Administrative Panel"
			pendingLabel="Pending Instructors"
			isAdminDashboard={true}
			requireRejectReason={true}
			pendingTotal={pendingTotal}
			actionError={actionError}
			pendingInstructors={pendingCount}
			approvedInstructors={adminStats?.approvedInstructors ?? 0}
			adminStats={adminStats}
		/>
	);
}

function InstructorDashboardRoute() {
	const { session } = useSessionStore();
	const token = session?.accessToken;
	const [instructorStats, setInstructorStats] = useState<InstructorStats | undefined>();
	const [requests, setRequests] = useState<DashboardRequest[]>([]);

	const loadRequests = useCallback(async (): Promise<DashboardRequest[]> => {
		if (!token) return [];
		return bookingService.getPendingRequests(token);
	}, [token]);

	const instructorData = useMemo(
		() => ({
			name: session?.user?.instructor_profile?.full_name || session?.user?.email || "Instrutor",
			rating: session?.user?.instructor_profile?.rating_avg || 5.0,
		}),
		[session?.user]
	);

	const loadInstructorStats = useCallback(async (): Promise<InstructorStats | undefined> => {
		if (!token) return undefined;
		try {
			const res = await httpClient.get<{
				total_lessons: number;
				total_hours: number;
				unique_students: number;
				pending_bookings: number;
			}>("/instructor/stats", { token });
			if (res.data) {
				return {
					totalLessons: res.data.total_lessons,
					totalHours: res.data.total_hours,
					uniqueStudents: res.data.unique_students,
					pendingBookings: res.data.pending_bookings,
				};
			}
		} catch (err) {
			console.error("Failed to load instructor stats:", err);
		}
		return undefined;
	}, [token]);

	useEffect(() => {
		let active = true;

		void loadInstructorStats().then((data) => {
			if (active && data) {
				setInstructorStats(data);
			}
		});

		void loadRequests()
			.then((nextRequests) => {
				if (active) setRequests(nextRequests);
			})
			.catch((err) => {
				console.error("Failed to load booking requests:", err);
			});

		return () => {
			active = false;
		};
	}, [loadInstructorStats, loadRequests]);

	const refresh = async () => {
		try {
			setRequests(await loadRequests());
		} catch (err) {
			console.error("Failed to reload booking requests:", err);
		}
		const stats = await loadInstructorStats();
		if (stats) setInstructorStats(stats);
	};

	// On failure (e.g. the request expired meanwhile), reload so the list shows the truth
	const answer = async (answerRequest: () => Promise<unknown>) => {
		try {
			await answerRequest();
		} catch (err) {
			console.error("Failed to answer booking request:", err);
		}
		await refresh();
	};

	const confirm = async (bookingId: string) => {
		if (!token) return;
		await answer(() => bookingService.confirmBooking(bookingId, token));
	};

	const decline = async (bookingId: string) => {
		if (!token) return;
		await answer(() =>
			bookingService.cancelBooking(bookingId, token, "Recusado pelo instrutor"),
		);
	};

	return (
		<InstructorDashboard
			instructorData={instructorData}
			requests={requests}
			onAccept={confirm}
			onReject={decline}
			agenda={
				<>
					<InstructorUpcomingLessons token={token} />
					<InstructorAgenda
						token={token}
						awaitingApproval={
							session?.user?.instructor_profile?.detran_status !== "APROVADO"
						}
					/>
				</>
			}
			dashboardTitle="Instructor Panel"
			pendingLabel="Minhas Reservas"
			instructorStats={instructorStats}
		/>
	);
}

function RootRedirect() {
	const { isAuthenticated, roles } = useSessionStore();
	if (!isAuthenticated) {
		return <Navigate to="/" replace />;
	}

	return <Navigate to={homePathFor(roles)} replace />;
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
				aria-label={
					isDark ? "Switch to light theme" : "Switch to dark theme"
				}
				title={
					isDark ? "Switch to light theme" : "Switch to dark theme"
				}
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

function MainLayout() {
	return (
		<Box minH="100vh" display="flex" flexDirection="column">
			<Navbar />
			<Box as="main" flex="1" pt="16">
				<Outlet />
			</Box>
			<Footer />
		</Box>
	);
}

export default function AppRouter() {
	return (
		<BrowserRouter>
			<Routes>
				<Route element={<MainLayout />}>
					<Route path="/" element={<HomeRoute />} />
					<Route path="/about" element={<About />} />
					<Route path="/contact" element={<Contact />} />
					<Route path="/help" element={<Help />} />
					<Route path="/terms" element={<Terms />} />
					<Route path="/privacy" element={<Privacy />} />

					{/* Students routes */}
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

					{/* Instructors routes */}
					<Route
						path="/instructors/how-it-works"
						element={<HowItWorksInstructor />}
					/>
					<Route
						path="/instructors/benefits"
						element={<Benefits />}
					/>
					<Route
						path="/instructors/simulator"
						element={<Simulator />}
					/>
					<Route
						path="/instructors/:id"
						element={<InstructorPublicProfilePage />}
					/>
					<Route
						path="/students/:id"
						element={<StudentPublicProfilePage />}
					/>

					{/* Protected search */}
					<Route
						path="/search"
						element={
							<ProtectedRoute>
								<SearchRoute />
							</ProtectedRoute>
						}
					/>

					<Route
						path="/bookings/new/:slug"
						element={
							<ProtectedRoute>
								<BookingDetailsRoute />
							</ProtectedRoute>
						}
					/>

					<Route
						path="/profile"
						element={
							<ProtectedRoute>
								<ProfileRoute />
							</ProtectedRoute>
						}
					/>
					<Route
						path="/my-lessons"
						element={
							<ProtectedRoute>
								<MyLessonsRoute />
							</ProtectedRoute>
						}
					/>

					<Route
						path="/instructor/dashboard"
						element={
							<ProtectedRoute>
								<RoleRoute roles={["INSTRUTOR"]}>
									<InstructorDashboardRoute />
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
				</Route>

				<Route path="/login" element={<LoginRoute />} />
				<Route path="/register" element={<RegisterRoute />} />
				<Route path="/password-reset" element={<PasswordReset />} />
				<Route path="/password-reset/confirm" element={<PasswordResetConfirm />} />

				<Route path="/app" element={<RootRedirect />} />
				<Route path="*" element={<RootRedirect />} />
			</Routes>
			<ColorModeToggle />
		</BrowserRouter>
	);
}
