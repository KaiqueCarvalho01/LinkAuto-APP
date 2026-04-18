import React from "react";
import ReactDOM from "react-dom/client";
import AppRouter from "./app/router.jsx";
import "./index.css";
import { SessionProvider } from "./state/sessionStore.js";

ReactDOM.createRoot(document.getElementById("root")).render(
	<React.StrictMode>
		<SessionProvider>
			<AppRouter />
		</SessionProvider>
	</React.StrictMode>,
);
