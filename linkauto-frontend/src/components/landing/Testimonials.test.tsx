import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";

import { Testimonials } from "./Testimonials";
import { renderWithProviders } from "../../test/renderWithProviders";

describe("Testimonials", () => {
	it("renders student testimonials by default", () => {
		renderWithProviders(<Testimonials />);

		expect(screen.getByText(/O que nossos alunos dizem/i)).toBeInTheDocument();
		// Check for a known mock student name (we'll create the mock data next)
		expect(screen.getByText(/Maria Silva/i)).toBeInTheDocument();
	});

	it("switches to instructor testimonials when tab is clicked", async () => {
		const user = userEvent.setup();
		renderWithProviders(<Testimonials />);

		const instructorTab = screen.getByRole("tab", { name: /Instrutores/i });
		await user.click(instructorTab);

		expect(screen.getByText(/A voz de quem ensina/i)).toBeInTheDocument();
		// Check for a known mock instructor name
		expect(screen.getByText(/Ricardo Santos/i)).toBeInTheDocument();
	});
});
