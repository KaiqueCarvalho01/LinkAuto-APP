import {
	createContext,
	useCallback,
	useContext,
	useMemo,
	useState,
	type ReactNode,
} from "react";

import type { ApiSuccessEnvelope } from "../types/api";
import type { AuthLoginResponse, SessionData, SignInInput, UserAccount } from "../types/session";
import { httpClient } from "../services/httpClient";

const SESSION_STORAGE_KEY = "linkauto.session.v1";

interface SessionContextValue {
	session: SessionData | null;
	isAuthenticated: boolean;
	roles: string[];
	signIn: (payload: SignInInput) => Promise<SessionData>;
	signUp: (payload: {
		email: string;
		password: string;
		roles: string[];
	}) => Promise<void>;
	signOut: () => void;
	clearSession: () => void;
	refreshProfile: (token: string) => Promise<ApiSuccessEnvelope<UserAccount>>;
}

interface SessionProviderProps {
	children: ReactNode;
}

const SessionContext = createContext<SessionContextValue | null>(null);

const isObjectRecord = (value: unknown): value is Record<string, unknown> => {
	return typeof value === "object" && value !== null;
};

const isSessionData = (value: unknown): value is SessionData => {
	if (!isObjectRecord(value)) {
		return false;
	}

	const accessToken = value.accessToken;
	const tokenType = value.tokenType;
	const user = value.user;
	if (typeof accessToken !== "string" || typeof tokenType !== "string" || !isObjectRecord(user)) {
		return false;
	}

	return typeof user.email === "string" && Array.isArray(user.roles);
};

const loadPersistedSession = (): SessionData | null => {
	const raw = localStorage.getItem(SESSION_STORAGE_KEY);
	if (!raw) {
		return null;
	}

	try {
		const parsed: unknown = JSON.parse(raw);
		if (isSessionData(parsed)) {
			return parsed;
		}
		localStorage.removeItem(SESSION_STORAGE_KEY);
		return null;
	} catch {
		localStorage.removeItem(SESSION_STORAGE_KEY);
		return null;
	}
};

const persistSession = (session: SessionData | null): void => {
	if (!session) {
		localStorage.removeItem(SESSION_STORAGE_KEY);
		return;
	}

	localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(session));
};

export function SessionProvider({ children }: SessionProviderProps) {
	const [session, setSession] = useState<SessionData | null>(() => loadPersistedSession());

	const clearSession = useCallback(() => {
		setSession(null);
		persistSession(null);
	}, []);

	const refreshProfile = useCallback(async (token: string) => {
		return httpClient.get<UserAccount>("/users/me", { token });
	}, []);

	const signIn = useCallback(
		async ({ email, password }: SignInInput) => {
			const loginPayload = await httpClient.post<AuthLoginResponse>("/auth/login", {
				email,
				password,
			});

			const mePayload = await refreshProfile(loginPayload.data.access_token);
			const nextSession: SessionData = {
				accessToken: loginPayload.data.access_token,
				tokenType: loginPayload.data.token_type,
				user: mePayload.data,
			};

			setSession(nextSession);
			persistSession(nextSession);
			return nextSession;
		},
		[refreshProfile],
	);

	const signUp = useCallback(
		async ({
			email,
			password,
			roles,
		}: {
			email: string;
			password: string;
			roles: string[];
		}) => {
			await httpClient.post("/auth/register", {
				email,
				password,
				roles,
			});
		},
		[],
	);

	const signOut = useCallback(() => {
		clearSession();
	}, [clearSession]);

	const value = useMemo<SessionContextValue>(
		() => ({
			session,
			isAuthenticated: Boolean(session?.accessToken),
			roles: session?.user?.roles ?? [],
			signIn,
			signUp,
			signOut,
			clearSession,
			refreshProfile,
		}),
		[session, signIn, signUp, signOut, clearSession, refreshProfile],
	);

	return <SessionContext value={value}>{children}</SessionContext>;
}

export function useSessionStore(): SessionContextValue {
	const context = useContext(SessionContext);
	if (!context) {
		throw new Error("useSessionStore must be used within SessionProvider");
	}

	return context;
}