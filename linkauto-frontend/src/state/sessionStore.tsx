import {
	createContext,
	useCallback,
	useContext,
	useMemo,
	useState,
	useEffect,
	type ReactNode,
} from "react";

import type { ApiSuccessEnvelope } from "../types/api";
import type { AuthLoginResponse, SessionData, SignInInput, UserAccount } from "../types/session";
import { httpClient, setOnTokenRefreshed, setOnAuthFailure } from "../services/httpClient";

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
		fullName?: string;
	}) => Promise<void>;
	signOut: () => Promise<void>;
	clearSession: () => void;
	refreshProfile: (token: string) => Promise<ApiSuccessEnvelope<UserAccount>>;
	// Replace the signed-in user (e.g. after a profile edit), in memory and in storage
	updateUser: (user: UserAccount) => void;
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

	const updateUser = useCallback((user: UserAccount) => {
		setSession((prev) => {
			if (!prev) return prev;
			const next = { ...prev, user };
			persistSession(next);
			return next;
		});
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
			fullName,
		}: {
			email: string;
			password: string;
			roles: string[];
			fullName?: string;
		}) => {
			await httpClient.post("/auth/register", {
				email,
				password,
				roles,
				full_name: fullName?.trim() || undefined,
			});
		},
		[],
	);

	const signOut = useCallback(async () => {
		// Clear locally first so the UI logs out immediately, even when offline
		clearSession();
		try {
			// Revokes the refresh token (HttpOnly cookie) on the server
			await httpClient.post("/auth/logout", {});
		} catch {
			// Best effort: the session is already gone locally
		}
	}, [clearSession]);

	useEffect(() => {
		setOnTokenRefreshed((newToken) => {
			setSession((prev) => {
				if (!prev) return null;
				const next = { ...prev, accessToken: newToken };
				persistSession(next);
				return next;
			});
		});
		setOnAuthFailure(() => {
			// The refresh token was rejected, so there is nothing left to revoke
			clearSession();
		});
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
			updateUser,
		}),
		[session, signIn, signUp, signOut, clearSession, refreshProfile, updateUser],
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