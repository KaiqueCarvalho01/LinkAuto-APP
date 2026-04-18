import React, {
	createContext,
	useCallback,
	useContext,
	useMemo,
	useState,
} from "react";
import { httpClient } from "../services/httpClient";

const SESSION_STORAGE_KEY = "linkauto.session.v1";

const SessionContext = createContext(null);

const loadPersistedSession = () => {
	const raw = localStorage.getItem(SESSION_STORAGE_KEY);
	if (!raw) return null;
	try {
		return JSON.parse(raw);
	} catch {
		localStorage.removeItem(SESSION_STORAGE_KEY);
		return null;
	}
};

const persistSession = (session) => {
	if (!session) {
		localStorage.removeItem(SESSION_STORAGE_KEY);
		return;
	}
	localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(session));
};

export function SessionProvider({ children }) {
	const [session, setSession] = useState(() => loadPersistedSession());

	const clearSession = useCallback(() => {
		setSession(null);
		persistSession(null);
	}, []);

	const refreshProfile = useCallback(async (token) => {
		return httpClient.get("/users/me", { token });
	}, []);

	const signIn = useCallback(
		async ({ email, password }) => {
			const loginPayload = await httpClient.post("/auth/login", {
				email,
				password,
			});
			const accessToken = loginPayload.data.access_token;
			const mePayload = await refreshProfile(accessToken);

			const nextSession = {
				accessToken,
				tokenType: loginPayload.data.token_type,
				user: mePayload.data,
			};
			setSession(nextSession);
			persistSession(nextSession);
			return nextSession;
		},
		[refreshProfile],
	);

	const signOut = useCallback(() => {
		clearSession();
	}, [clearSession]);

	const value = useMemo(
		() => ({
			session,
			isAuthenticated: Boolean(session?.accessToken),
			roles: session?.user?.roles ?? [],
			signIn,
			signOut,
			clearSession,
			setSession,
			refreshProfile,
		}),
		[session, signIn, signOut, clearSession, refreshProfile],
	);

	return React.createElement(SessionContext.Provider, { value }, children);
}

export function useSessionStore() {
	const context = useContext(SessionContext);
	if (!context) {
		throw new Error("useSessionStore must be used within SessionProvider");
	}
	return context;
}
