import { screen } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";

import { renderWithProviders } from "../test/renderWithProviders";
import Register from "./Register";
import About from "./About";
import Contact from "./Contact";
import Help from "./Help";
import Home from "./Home";
import InstructorDashboard from "./InstructorDashboard";
import LessonDetails from "./LessonDetails";
import MyLessons from "./MyLessons";
import Profile from "./Profile";
import SearchPage from "./SearchPage";
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
		expect(screen.getByText(/About/i)).toBeInTheDocument();
	});

	it("renders Contact page", () => {
		renderWithProviders(<Contact />);
		expect(screen.getByText(/Contact/i)).toBeInTheDocument();
	});

	it("renders Help page", () => {
		renderWithProviders(<Help />);
		expect(screen.getByText(/Help/i)).toBeInTheDocument();
	});

	it("renders Home page", () => {
		renderWithProviders(
			<Home
				isAuthenticated={false}
				onOpenLogin={vi.fn()}
				onOpenSearch={vi.fn()}
			/>,
		);
		expect(screen.getByText(/A liberdade de dirigir/i)).toBeInTheDocument();
	});

	it("renders InstructorDashboard page", () => {
		renderWithProviders(<InstructorDashboard />);
		expect(screen.getByText(/Painel do Instrutor/i)).toBeInTheDocument();
	});

	it("renders LessonDetails page", () => {
		renderWithProviders(
			<LessonDetails
				instructor={{
					id: "1",
					fullName: "Teste",
					rating: 5,
					hourlyRate: 80,
					specialties: [],
					city: "",
					neighborhood: "",
					reviewsCount: 0,
					distanceKm: 0,
					detranApproved: true,
					radiusKm: 5,
					coordinates: { lat: 0, lng: 0 },
				}}
				onBack={vi.fn()}
				onBookingCreated={vi.fn()}
			/>,
		);
		expect(
			screen.getAllByText(/Solicitar agendamento/i).length,
		).toBeGreaterThanOrEqual(1);
	});

	it("renders MyLessons page", () => {
		renderWithProviders(<MyLessons onNewBooking={vi.fn()} />);
		expect(screen.getByText(/Meus agendamentos/i)).toBeInTheDocument();
	});

	it("renders Profile page", () => {
		renderWithProviders(
			<Profile
				onLogout={vi.fn()}
				onNavigateToSearch={vi.fn()}
				onNavigateToBookings={vi.fn()}
				onNavigateToVehicles={vi.fn()}
			/>,
		);
		expect(screen.getByText(/Conta LinkAuto/i)).toBeInTheDocument();
	});

	it("renders SearchPage page", () => {
		renderWithProviders(
			<SearchPage
				token="test"
				onOpenProfile={vi.fn()}
				onStartBooking={vi.fn()}
			/>,
		);
		expect(screen.getByText(/Buscar instrutores/i)).toBeInTheDocument();
	});

	it("renders FirstLicense page", () => {
		renderWithProviders(<FirstLicense />);
		expect(screen.getByText(/Sua CNH com/i)).toBeInTheDocument();
		expect(screen.getByText(/Liberdade/i)).toBeInTheDocument();
	});

	it("renders LicensedDrivers page", () => {
		renderWithProviders(<LicensedDrivers />);
		expect(
			screen.getByText(/Volte a Dirigir com Confiança/i),
		).toBeInTheDocument();
	});

	it("renders students HowItWorks page", () => {
		renderWithProviders(<HowItWorksStudent />);
		expect(
			screen.getByText(/O Caminho para a Autonomia/i),
		).toBeInTheDocument();
	});

	it("renders instructors HowItWorks page", () => {
		renderWithProviders(<HowItWorksInstructor />);
		expect(screen.getByText(/Seu novo escritório/i)).toBeInTheDocument();
	});

	it("renders Benefits page", () => {
		renderWithProviders(<Benefits />);
		expect(
			screen.getByText(/Seja dono da sua agenda/i),
		).toBeInTheDocument();
	});

	it("renders Simulator page", () => {
		renderWithProviders(<Simulator />);
		expect(screen.getByText(/Potencial de Ganhos/i)).toBeInTheDocument();
	});
});
