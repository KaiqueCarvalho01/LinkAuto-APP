import { httpClient } from "./httpClient";
import { mapApiReviewToFrontend } from "./instructorService";
import type { ApiReviewResource } from "../types/api.types";
import type { BookingReview } from "../types/booking";

export const reviewService = {
  submitReview: async (
    bookingId: string,
    rating: number,
    comment: string | null,
    token: string
  ): Promise<BookingReview> => {
    const response = await httpClient.post<ApiReviewResource>(
      `/bookings/${bookingId}/reviews`,
      { rating, comment },
      { token }
    );
    return mapApiReviewToFrontend(response.data);
  },
};
