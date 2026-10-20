import { screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { RatingStars } from "./RatingStars";
import { renderWithProviders } from "../test/renderWithProviders";

describe("RatingStars", () => {
	it("shows the average and the number of reviews", () => {
		renderWithProviders(<RatingStars rating={4.86} reviewsCount={12} />);

		expect(screen.getByText("4.9 (12 avaliações)")).toBeInTheDocument();
	});

	it("says there are no reviews instead of showing a 0.0 rating", () => {
		renderWithProviders(<RatingStars rating={0} reviewsCount={0} />);

		expect(screen.getByText("Sem avaliações")).toBeInTheDocument();
		expect(screen.queryByText(/0\.0/)).not.toBeInTheDocument();
	});
});
