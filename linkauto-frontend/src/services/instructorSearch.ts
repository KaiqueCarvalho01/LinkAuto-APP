import { httpClient } from "./httpClient";
import { mockInstructors } from "./mockData";
import type {
	InstructorSearchParams,
	InstructorSummary,
} from "../types/instructor";

interface InstructorSearchApiItem {
	id: string;
	full_name?: string;
	city?: string;
	neighborhood?: string;
	rating?: number;
	reviews_count?: number;
	distance_km?: number;
	hourly_rate?: number;
	detran_status?: string;
	specialties?: string[];
	radius_km?: number;
	coordinates?: {
		lat?: number;
		lng?: number;
	};
}

const normalizeText = (value: string): string => value.trim().toLowerCase();

const mapApiInstructor = (
	item: InstructorSearchApiItem,
): InstructorSummary => ({
	id: item.id,
	fullName: item.full_name ?? "Instrutor LinkAuto",
	city: item.city ?? "Cidade nao informada",
	neighborhood: item.neighborhood ?? "Bairro nao informado",
	rating: item.rating ?? 4.5,
	reviewsCount: item.reviews_count ?? 0,
	distanceKm: item.distance_km ?? 0,
	hourlyRate: item.hourly_rate ?? 90,
	detranApproved: item.detran_status === "APROVADO",
	specialties: item.specialties ?? ["Primeira habilitacao"],
	radiusKm: item.radius_km ?? 8,
	coordinates: {
		lat: item.coordinates?.lat ?? -22.4331,
		lng: item.coordinates?.lng ?? -46.957,
	},
});

const filterByParams = (
	instructors: InstructorSummary[],
	params: InstructorSearchParams,
): InstructorSummary[] => {
	const query = normalizeText(params.query);
	const city = normalizeText(params.city);
	const specialty = normalizeText(params.specialty);

	return instructors
		.filter((instructor) => {
			const cityMatch =
				city.length === 0 ||
				normalizeText(instructor.city).includes(city) ||
				normalizeText(instructor.neighborhood).includes(city);

			const textMatch =
				query.length === 0 ||
				normalizeText(instructor.fullName).includes(query) ||
				instructor.specialties.some((topic) =>
					normalizeText(topic).includes(query),
				);

			const specialtyMatch =
				specialty.length === 0 ||
				specialty === "todas" ||
				instructor.specialties.some(
					(topic) => normalizeText(topic) === specialty,
				);

			const distanceMatch = instructor.distanceKm <= params.radiusKm;
			const ratingMatch = instructor.rating >= params.minRating;

			return (
				cityMatch &&
				textMatch &&
				specialtyMatch &&
				distanceMatch &&
				ratingMatch
			);
		})
		.sort((a, b) => a.distanceKm - b.distanceKm);
};

export const searchInstructors = async (
	params: InstructorSearchParams,
	token?: string,
): Promise<InstructorSummary[]> => {
	try {
		if (!token) {
			throw new Error("Session token not available");
		}

		const queryParams = new URLSearchParams();
		if (params.query.trim()) {
			queryParams.set("q", params.query.trim());
		}
		if (params.city.trim()) {
			queryParams.set("city", params.city.trim());
		}
		if (params.specialty.trim() && params.specialty !== "Todas") {
			queryParams.set("specialty", params.specialty.trim());
		}
		queryParams.set("radius_km", String(params.radiusKm));

		const path = `/instructors/search?${queryParams.toString()}`;
		const payload = await httpClient.get<InstructorSearchApiItem[]>(path, {
			token,
		});

		if (!Array.isArray(payload.data) || payload.data.length === 0) {
			return filterByParams(mockInstructors, params);
		}

		return filterByParams(payload.data.map(mapApiInstructor), params);
	} catch {
		return filterByParams(mockInstructors, params);
	}
};
