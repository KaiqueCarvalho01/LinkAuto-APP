import { screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { Footer } from "./Footer";
import { renderWithProviders } from "../test/renderWithProviders";

describe("Footer", () => {
	it("should render the footer component", () => {
		renderWithProviders(<Footer />);
		expect(screen.getByRole("contentinfo")).toBeInTheDocument();
	});

	it("should display the LinkAuto logo and copyright text", () => {
		renderWithProviders(<Footer />);
		expect(screen.getByText(/© 2026 LinkAuto\. All rights reserved\./i)).toBeInTheDocument();
	});

	it("should have three columns of links: Students, Instructors, and Institutional", () => {
		renderWithProviders(<Footer />);
		expect(screen.getByText(/Students/i)).toBeInTheDocument();
		expect(screen.getByText(/Instructors/i)).toBeInTheDocument();
		expect(screen.getByText(/Institutional/i)).toBeInTheDocument();
	});

	it("should have the correct links under the Students column", () => {
		renderWithProviders(<Footer />);
		expect(screen.getByRole("link", { name: /First License/i })).toHaveAttribute("href", "/students/first-license");
		expect(screen.getByRole("link", { name: /Find an Instructor/i })).toHaveAttribute("href", "/search");
		expect(screen.getByRole("link", { name: /My Lessons/i })).toHaveAttribute("href", "/student/lessons");
	});

	it("should have the correct links under the Instructors column", () => {
		renderWithProviders(<Footer />);
		expect(screen.getByRole("link", { name: /Register as Instructor/i })).toHaveAttribute("href", "/instructors/register");
		expect(screen.getByRole("link", { name: /My Students/i })).toHaveAttribute("href", "/instructor/students");
		expect(screen.getByRole("link", { name: /My Vehicles/i })).toHaveAttribute("href", "/instructor/vehicles");
	});

	it("should have the correct links under the Institutional column", () => {
		renderWithProviders(<Footer />);
		expect(screen.getByRole("link", { name: /About Us/i })).toHaveAttribute("href", "/about");
		expect(screen.getByRole("link", { name: /Contact/i })).toHaveAttribute("href", "/contact");
		expect(screen.getByRole("link", { name: /Terms of Service/i })).toHaveAttribute("href", "/terms");
	});
});
