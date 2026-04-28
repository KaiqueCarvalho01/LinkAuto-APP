import { describe, expect, it } from "vitest";
import { screen } from "@testing-library/react";

import { BookingStatusBadge, bookingStatusLabel } from "./BookingStatusBadge";
import { renderWithProviders } from "../test/renderWithProviders";

describe("BookingStatusBadge", () => {
	it("maps labels correctly", () => {
		expect(bookingStatusLabel("PENDENTE")).toBe("Pendente");
		expect(bookingStatusLabel("CONFIRMADA")).toBe("Confirmada");
		expect(bookingStatusLabel("REALIZADA")).toBe("Realizada");
		expect(bookingStatusLabel("CANCELADA")).toBe("Cancelada");
	});

	it("renders semantic aria label for status", () => {
		renderWithProviders(<BookingStatusBadge status="CONFIRMADA" />);

		expect(screen.getByLabelText("Status Confirmada")).toBeInTheDocument();
		expect(screen.getByText("Confirmada")).toBeInTheDocument();
	});
});
