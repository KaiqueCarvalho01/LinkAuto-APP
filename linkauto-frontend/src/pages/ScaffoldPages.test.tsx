import { screen } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";

import { renderWithProviders } from "../test/renderWithProviders";
import Register from "./Register";
import About from "./About";
import Contact from "./Contact";
import Notifications from "./Notifications";
import Help from "./Help";
import AuditLog from "./admin/AuditLog";
import FirstLicense from "./students/FirstLicense";
import LicensedDrivers from "./students/LicensedDrivers";
import HowItWorksStudent from "./students/HowItWorks";
import HowItWorksInstructor from "./instructors/HowItWorks";
import Benefits from "./instructors/Benefits";
import Simulator from "./instructors/Simulator";

describe("Scaffold Pages", () => {
	it("renders Register page", () => {
		renderWithProviders(<Register onRegister={vi.fn()} />);
		expect(screen.getByText(/Crie sua conta/i)).toBeInTheDocument();
	});

	it("renders About page", () => {
		renderWithProviders(<About />);
		expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(
			"About",
		);
	});

	it("renders Contact page", () => {
		renderWithProviders(<Contact />);
		expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(
			"Contact",
		);
	});

	it("renders Notifications page", () => {
		renderWithProviders(<Notifications />);
		expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(
			"Notifications",
		);
	});

	it("renders Help page", () => {
		renderWithProviders(<Help />);
		expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(
			"Help",
		);
	});

	it("renders AuditLog page", () => {
		renderWithProviders(<AuditLog />);
		expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(
			"Audit Log",
		);
	});

	it("renders FirstLicense page", () => {
		renderWithProviders(<FirstLicense />);
		expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(
			"First License",
		);
	});

	it("renders LicensedDrivers page", () => {
		renderWithProviders(<LicensedDrivers />);
		expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(
			"Licensed Drivers",
		);
	});

	it("renders students HowItWorks page", () => {
		renderWithProviders(<HowItWorksStudent />);
		expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(
			"How It Works for Students",
		);
	});

	it("renders instructors HowItWorks page", () => {
		renderWithProviders(<HowItWorksInstructor />);
		expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(
			"How It Works for Instructors",
		);
	});

	it("renders Benefits page", () => {
		renderWithProviders(<Benefits />);
		expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(
			"Benefits",
		);
	});

	it("renders Simulator page", () => {
		renderWithProviders(<Simulator />);
		expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(
			"Simulator",
		);
	});
});
