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
  latitude?: number | undefined;
  longitude?: number | undefined;
  radiusKm?: number | undefined;
  minRating?: number | undefined;
  maxPrice?: number | undefined;
  specialty?: string | undefined;
  specialties?: string[] | undefined;
  sortBy?: "rating" | "price_asc" | "price_desc" | "distance" | undefined;
  query?: string | undefined;
  city?: string | undefined;
}
