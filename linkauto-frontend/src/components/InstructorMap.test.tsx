import { screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { InstructorMap } from "./InstructorMap";
import { renderWithProviders } from "../test/renderWithProviders";
import type { InstructorSummary } from "../types/instructor";

const instructor = (
	slug: string,
	fullName: string,
	coordinates: InstructorSummary["coordinates"],
): InstructorSummary => ({
	id: slug,
	slug,
	fullName,
	city: "Mogi Mirim",
	neighborhood: "SP",
	rating: 0,
	reviewsCount: 0,
	distanceKm: 0,
	hourlyRate: 80,
	detranApproved: true,
	specialties: [],
	radiusKm: 10,
	coordinates,
});

describe("InstructorMap", () => {
	it("leaves out instructors without coordinates instead of placing them at (0, 0)", () => {
		renderWithProviders(
			<InstructorMap
				instructors={[
					instructor("sem-mapa", "Sem Mapa", null),
					instructor("com-mapa", "Com Mapa", { lat: -22.43, lng: -46.95 }),
				]}
				selectedInstructorId={undefined}
				onSelect={vi.fn()}
				onBook={vi.fn()}
			/>,
		);

		expect(screen.getByText("CM")).toBeInTheDocument();
		expect(screen.queryByText("SM")).not.toBeInTheDocument();
		expect(screen.getByText(/Raio de atendimento de Com Mapa/)).toBeInTheDocument();
	});
});
