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

describe("RatingStars for screen readers", () => {
	it("hides the decorative stars, since the text already says the rating", () => {
		const { container } = renderWithProviders(<RatingStars rating={4} reviewsCount={3} />);

		for (const icon of container.querySelectorAll("svg")) {
			expect(icon.closest("[aria-hidden='true']")).not.toBeNull();
		}
		expect(screen.getByText("4.0 (3 avaliações)")).toBeInTheDocument();
		// aria-label on a plain div is ignored by screen readers (and not allowed by ARIA)
		expect(container.querySelector("div[aria-label]:not([role])")).toBeNull();
	});
});
