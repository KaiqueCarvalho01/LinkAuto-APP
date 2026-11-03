import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import Home from "./Home";
import type { InstructorSummary } from "../types/instructor";
import { instructorService } from "../services/instructorService";
import { mockInstructors } from "../test/fixtures/mockData";
import { renderWithProviders } from "../test/renderWithProviders";

vi.mock("../components/InstructorMap", () => ({
	InstructorMap: ({
		instructors,
		onBook,
	}: {
		instructors: InstructorSummary[];
		onBook: (instructor: InstructorSummary) => void;
	}) => (
		<div>
			{instructors.map((instructor) => (
				<button key={instructor.id} type="button" onClick={() => onBook(instructor)}>
					Agendar {instructor.fullName}
				</button>
			))}
		</div>
	),
}));

const renderHome = (props: Partial<React.ComponentProps<typeof Home>> = {}) =>
	renderWithProviders(
		<Home
			isAuthenticated={false}
			onOpenLogin={vi.fn()}
			onOpenSearch={vi.fn()}
			onBookInstructor={vi.fn()}
			{...props}
		/>,
	);

describe("Home instructor map", () => {
	beforeEach(() => {
		vi.restoreAllMocks();
	});

	it("never fills the map with made-up instructors when there are none", async () => {
		vi.spyOn(instructorService, "getPublicInstructors").mockResolvedValue([]);

		renderHome();

		expect(
			await screen.findByText("Ainda não há instrutores disponíveis no mapa."),
		).toBeInTheDocument();
		expect(screen.queryByText("Modo Demonstração")).not.toBeInTheDocument();
	});

	it("says the instructors couldn't be loaded when the request fails", async () => {
		vi.spyOn(instructorService, "getPublicInstructors").mockRejectedValue(
			new Error("Network down"),
		);

		renderHome();

		expect(
			await screen.findByText("Não foi possível carregar os instrutores."),
		).toBeInTheDocument();
		expect(screen.queryByText("Modo Demonstração")).not.toBeInTheDocument();
	});

	it("books the instructor picked on the map instead of opening the search", async () => {
		const [instructor] = mockInstructors;
		vi.spyOn(instructorService, "getPublicInstructors").mockResolvedValue([instructor!]);
		const onOpenSearch = vi.fn();
		const onBookInstructor = vi.fn();

		renderHome({ onOpenSearch, onBookInstructor });
		await userEvent.click(
			await screen.findByRole("button", { name: `Agendar ${instructor!.fullName}` }),
		);

		expect(onBookInstructor).toHaveBeenCalledWith(instructor);
		expect(onOpenSearch).not.toHaveBeenCalled();
	});
});
