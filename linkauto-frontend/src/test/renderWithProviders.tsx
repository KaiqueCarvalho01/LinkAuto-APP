import type { ReactElement } from "react";
import { render } from "@testing-library/react";
import { ChakraProvider } from "@chakra-ui/react";

import { appSystem } from "../theme/system";

export const renderWithProviders = (ui: ReactElement) => {
	return render(<ChakraProvider value={appSystem}>{ui}</ChakraProvider>);
};
