import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";

import { Navbar } from "./Navbar";
import { renderWithProviders } from "../test/renderWithProviders";

describe("Navbar (Visitor State)", () => {
	it("renders main navigation links for visitors", () => {
		renderWithProviders(<Navbar />);

		expect(
screen.getByRole("link", { name: /Explore/i }),
).toBeInTheDocument();
		expect(
screen.getByRole("button", { name: /For Students/i }),
).toBeInTheDocument();
		expect(
screen.getByRole("button", { name: /For Instructors/i }),
).toBeInTheDocument();
		expect(
screen.getByRole("link", { name: /About/i }),
).toBeInTheDocument();
		expect(
screen.getByRole("link", { name: /Contact/i }),
).toBeInTheDocument();
		expect(
screen.getByRole("link", { name: /Log In/i }),
).toBeInTheDocument();
		expect(
screen.getByRole("link", { name: /Sign Up/i }),
).toBeInTheDocument();
	});

	it("opens 'For Students' dropdown menu", async () => {
		const user = userEvent.setup();
		renderWithProviders(<Navbar />);

		const menuButton = screen.getByRole("button", { name: /For Students/i });
		await user.click(menuButton);

		expect(
screen.getByRole("link", { name: /First License/i }),
).toBeInTheDocument();
		expect(
screen.getByRole("link", { name: /Licensed Drivers/i }),
).toBeInTheDocument();
		expect(
screen.getByRole("link", { name: /How it Works/i }),
).toBeInTheDocument();
		expect(
screen.getByRole("link", { name: /Find Instructors/i }),
).toBeInTheDocument();
	});

	it("opens 'For Instructors' dropdown menu", async () => {
		const user = userEvent.setup();
		renderWithProviders(<Navbar />);

		const menuButton = screen.getByRole("button", {
name: /For Instructors/i,
});
		await user.click(menuButton);

		expect(
screen.getByRole("link", { name: /Register Now/i }),
).toBeInTheDocument();
		expect(
screen.getByRole("link", { name: /How it Works/i }),
).toBeInTheDocument();
		expect(
screen.getByRole("link", { name: /Benefits/i }),
).toBeInTheDocument();
		expect(
screen.getByRole("link", { name: /Simulator/i }),
).toBeInTheDocument();
	});
});
