export interface InstructorSummary {
	id: string;
	fullName: string;
	city: string;
	neighborhood: string;
	rating: number;
	reviewsCount: number;
	distanceKm: number;
	hourlyRate: number;
	detranApproved: boolean;
	specialties: string[];
	radiusKm: number;
	coordinates: {
		lat: number;
		lng: number;
	};
}

export interface InstructorSearchParams {
	query: string;
	city: string;
	specialty: string;
	radiusKm: number;
	minRating: number;
}
