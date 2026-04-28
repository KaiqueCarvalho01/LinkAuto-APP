import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { ChakraProvider } from "@chakra-ui/react";

import AppRouter from "./app/router";
import { SessionProvider } from "./state/sessionStore";
import { appSystem } from "./theme/system";
import "./index.css";

createRoot(document.getElementById("root") as HTMLElement).render(
	<StrictMode>
		<ChakraProvider value={appSystem}>
			<SessionProvider>
				<AppRouter />
			</SessionProvider>
		</ChakraProvider>
	</StrictMode>,
);
