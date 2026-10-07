import { httpClient } from "./httpClient";
import type {
  ApiInstructorSearchResult,
  ApiPublicInstructor,
  ApiReviewResource,
} from "../types/api.types";
import type { InstructorSummary, InstructorSearchParams } from "../types/instructor";
import type { BookingReview } from "../types/booking";

// Helper to calculate Haversine distance in KM
export const calculateDistance = (
  lat1: number,
  lon1: number,
  lat2: number,
  lon2: number
): number => {
  const R = 6371; // Earth radius in km
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLon = ((lon2 - lon1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return parseFloat((R * c).toFixed(1));
};

export const mapApiInstructorToSummary = (
  api: ApiInstructorSearchResult,
  userLat?: number,
  userLng?: number
): InstructorSummary => {
  const distance =
    userLat !== undefined && userLng !== undefined
      ? calculateDistance(userLat, userLng, api.latitude, api.longitude)
      : 0.0;

  const publicSlug = api.slug || api.id || (api.user_id as string);
  return {
    id: publicSlug,
    slug: publicSlug,
    fullName: api.full_name,
    city: api.city,
    neighborhood: api.state || "SP",
    rating: api.rating_avg,
    reviewsCount: api.rating_count,
    distanceKm: distance,
    hourlyRate: typeof api.price_per_hour === "string" ? parseFloat(api.price_per_hour) : api.price_per_hour ?? 0.0,
    detranApproved: true,
    specialties: api.specialties,
    radiusKm: api.action_radius_km,
    coordinates: {
      lat: api.latitude,
      lng: api.longitude,
    },
  };
};

export const mapApiReviewToFrontend = (api: ApiReviewResource): BookingReview => {
  return {
    id: api.id,
    bookingId: api.booking_id,
    reviewerId: api.reviewer_id,
    reviewedId: api.reviewed_id,
    rating: api.rating,
    comment: api.comment,
    createdAt: api.created_at,
  };
};

export const instructorService = {
  searchInstructors: async (
    params: InstructorSearchParams,
    token?: string
  ): Promise<InstructorSummary[]> => {
    // Latitude and longitude are mandatory for backend search, fallback to Mogi Mirim
    const lat = params.latitude ?? -22.4319;
    const lng = params.longitude ?? -46.9578;
    const radius = params.radiusKm ?? 20;

    const queryParams = new URLSearchParams();
    queryParams.set("latitude", lat.toString());
    queryParams.set("longitude", lng.toString());
    queryParams.set("radius_km", radius.toString());

    if (params.minRating !== undefined && params.minRating > 0) {
      queryParams.set("min_rating", params.minRating.toString());
    }

    if (params.maxPrice !== undefined && params.maxPrice > 0) {
      queryParams.set("max_price", params.maxPrice.toString());
    }

    if (params.specialties && params.specialties.length > 0) {
      for (const spec of params.specialties) {
        if (spec && spec !== "Todas") {
          queryParams.append("specialties", spec);
        }
      }
    } else if (params.specialty && params.specialty !== "Todas") {
      queryParams.append("specialties", params.specialty);
    }

    if (params.sortBy) {
      queryParams.set("sort_by", params.sortBy);
    }

    const response = await httpClient.get<ApiInstructorSearchResult[]>(
      `/instructors/search?${queryParams.toString()}`,
      token ? { token } : {}
    );

    const list = response.data || [];
    const mapped = list.map((item) => mapApiInstructorToSummary(item, lat, lng));
    return mapped;
  },

  getPublicInstructors: async (): Promise<InstructorSummary[]> => {
    const response = await httpClient.get<ApiPublicInstructor[]>("/users/public-instructors");
    const list = response.data || [];

    return list.map((item) => ({
      id: item.slug,
      slug: item.slug,
      fullName: item.full_name || "Instrutor",
      city: item.city || "",
      neighborhood: item.state || "SP",
      rating: item.rating_avg || 0.0,
      reviewsCount: item.rating_count || 0,
      distanceKm: 0.0,
      hourlyRate: item.price_per_hour ?? 0.0,
      detranApproved: true,
      specialties: item.specialties || [],
      radiusKm: item.action_radius_km || 10,
      coordinates: {
        lat: item.latitude ?? 0.0,
        lng: item.longitude ?? 0.0,
      },
    }));
  },

  getInstructorReviews: async (
    instructorId: string,
    page = 1
  ): Promise<BookingReview[]> => {
    const response = await httpClient.get<ApiReviewResource[]>(
      `/instructors/${instructorId}/reviews?page=${page}&page_size=20`
    );
    const list = response.data || [];
    return list.map(mapApiReviewToFrontend);
  },
};
