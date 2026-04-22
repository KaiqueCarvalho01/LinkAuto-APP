import type { ReactElement } from "react";
import { render } from "@testing-library/react";
import { ChakraProvider } from "@chakra-ui/react";
import { MemoryRouter } from "react-router-dom";

import { appSystem } from "../theme/system";

export const renderWithProviders = (ui: ReactElement) => {
	return render(
		<MemoryRouter>
			<ChakraProvider value={appSystem}>{ui}</ChakraProvider>
		</MemoryRouter>,
	);
};
