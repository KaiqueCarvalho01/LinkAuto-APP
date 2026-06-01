import { httpClient } from "./httpClient";
import type { ApiSlotResource } from "../types/api.types";
import type { BookingSlot, SlotState } from "../types/booking";

export const formatSlotLabel = (startsAtStr: string, endsAtStr: string): string => {
  try {
    const startsAt = new Date(startsAtStr);
    const endsAt = new Date(endsAtStr);
    
    // Using UTC because backend is strict ISO 8601 UTC Z format
    const startHour = String(startsAt.getUTCHours()).padStart(2, "0");
    const startMin = String(startsAt.getUTCMinutes()).padStart(2, "0");
    const endHour = String(endsAt.getUTCHours()).padStart(2, "0");
    const endMin = String(endsAt.getUTCMinutes()).padStart(2, "0");
    
    return `${startHour}:${startMin} - ${endHour}:${endMin}`;
  } catch {
    return "Horário";
  }
};

export const mapApiSlotToFrontend = (api: ApiSlotResource): BookingSlot => {
  return {
    id: api.id,
    label: formatSlotLabel(api.starts_at, api.ends_at),
    startAt: api.starts_at,
    endAt: api.ends_at,
    state: api.status as SlotState,
  };
};

export const slotService = {
  getInstructorSlots: async (instructorId: string): Promise<BookingSlot[]> => {
    const response = await httpClient.get<ApiSlotResource[]>(
      `/instructors/${instructorId}/slots`
    );
    const list = response.data || [];
    return list.map(mapApiSlotToFrontend);
  },

  getMySlots: async (token: string): Promise<BookingSlot[]> => {
    const response = await httpClient.get<ApiSlotResource[]>(
      "/instructors/me/slots",
      { token }
    );
    const list = response.data || [];
    return list.map(mapApiSlotToFrontend);
  },

  createSlot: async (
    data: { starts_at: string; ends_at: string },
    token: string
  ): Promise<BookingSlot> => {
    const response = await httpClient.post<ApiSlotResource>(
      "/instructors/me/slots",
      data,
      { token }
    );
    return mapApiSlotToFrontend(response.data);
  },

  deleteSlot: async (slotId: string, token: string): Promise<{ deleted: boolean }> => {
    const response = await httpClient.delete<{ deleted: boolean }>(
      `/instructors/me/slots/${slotId}`,
      { token }
    );
    return response.data;
  },
};
