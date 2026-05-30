import { httpClient } from "./httpClient";
import type { ApiMessageResource } from "../types/api.types";
import type { BookingMessage } from "../types/booking";

export const mapApiMessageToFrontend = (api: ApiMessageResource): BookingMessage => {
  return {
    id: api.id,
    bookingId: api.booking_id,
    senderId: api.sender_id,
    content: api.content,
    createdAt: api.created_at,
  };
};

export const messageService = {
  getBookingMessages: async (
    bookingId: string,
    token: string,
    page = 1
  ): Promise<BookingMessage[]> => {
    const response = await httpClient.get<ApiMessageResource[]>(
      `/bookings/${bookingId}/messages?page=${page}&page_size=50`,
      { token }
    );
    const list = response.data || [];
    return list.map(mapApiMessageToFrontend);
  },

  sendMessage: async (
    bookingId: string,
    content: string,
    token: string
  ): Promise<BookingMessage> => {
    const response = await httpClient.post<ApiMessageResource>(
      `/bookings/${bookingId}/messages`,
      { content },
      { token }
    );
    return mapApiMessageToFrontend(response.data);
  },
};
