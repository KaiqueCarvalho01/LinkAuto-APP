import { describe, expect, it } from "vitest";

import {
	instructorTestimonials,
	studentTestimonials,
} from "./staticContent";

describe("staticContent testimonials", () => {
	it("does not claim the platform processes payments (RN06)", () => {
		const allTestimonials = [...studentTestimonials, ...instructorTestimonials];

		for (const testimonial of allTestimonials) {
			expect(testimonial.text).not.toMatch(/pagamento/i);
			expect(testimonial.text).not.toMatch(/repasse/i);
		}
	});
});
