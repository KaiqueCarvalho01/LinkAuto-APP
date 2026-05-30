import { httpClient } from "./httpClient";
import { instructorService } from "./instructorService";
import type { ApiBookingResource } from "../types/api.types";
import type { BookingPreview, BookingStatus } from "../types/booking";
import type { InstructorSummary } from "../types/instructor";

export const formatDateLabel = (dateStr: string): string => {
  try {
    const date = new Date(dateStr);
    
    // Format: DD/MM/YYYY using UTC because backend returns strict UTC times
    const day = String(date.getUTCDate()).padStart(2, "0");
    const month = String(date.getUTCMonth() + 1).padStart(2, "0");
    const year = date.getUTCFullYear();
    
    const weekdays = [
      "Domingo",
      "Segunda-feira",
      "Terça-feira",
      "Quarta-feira",
      "Quinta-feira",
      "Sexta-feira",
      "Sábado",
    ];
    const weekday = weekdays[date.getUTCDay()];
    
    return `${weekday}, ${day}/${month}/${year}`;
  } catch {
    return "Data da aula";
  }
};

export const formatTimeLabel = (slots: ApiBookingResource["slots"]): string => {
  if (!slots || slots.length === 0) {
    return "Horário não definido";
  }
  
  try {
    // Sort slots chronologically
    const sorted = [...slots].sort(
      (a, b) => new Date(a.slot.starts_at).getTime() - new Date(b.slot.starts_at).getTime()
    );
    
    const firstSlot = sorted[0]?.slot;
    const lastSlot = sorted[sorted.length - 1]?.slot;
    
    if (!firstSlot || !lastSlot) {
      return "Horário não definido";
    }
    
    const first = new Date(firstSlot.starts_at);
    const last = new Date(lastSlot.ends_at);
    
    const startHour = String(first.getUTCHours()).padStart(2, "0");
    const startMin = String(first.getUTCMinutes()).padStart(2, "0");
    const endHour = String(last.getUTCHours()).padStart(2, "0");
    const endMin = String(last.getUTCMinutes()).padStart(2, "0");
    
    return `${startHour}:${startMin} - ${endHour}:${endMin}`;
  } catch {
    return "Horário da aula";
  }
};

export const mapApiBookingToPreview = (
  api: ApiBookingResource,
  instructors: InstructorSummary[]
): BookingPreview => {
  let instructor = instructors.find((inst) => inst.id === api.instructor_id);
  
  if (!instructor) {
    // Fallback instructor summary to avoid crashes
    instructor = {
      id: api.instructor_id,
      fullName: "Instrutor LinkAuto",
      city: "Mogi Mirim",
      neighborhood: "Centro",
      rating: 5.0,
      reviewsCount: 1,
      distanceKm: 0.0,
      hourlyRate: 70.0,
      detranApproved: true,
      specialties: ["Carro"],
      radiusKm: 10,
      coordinates: { lat: 0.0, lng: 0.0 },
    };
  }

  // Get date and time from the first slot
  const firstBookingSlot = api.slots?.[0];
  const dateStr = firstBookingSlot ? firstBookingSlot.slot.starts_at : api.created_at;
  
  return {
    id: api.id,
    instructor,
    dateLabel: formatDateLabel(dateStr),
    timeLabel: formatTimeLabel(api.slots),
    status: api.status as BookingStatus,
    cancellationReason: api.cancellation_reason ?? undefined,
  };
};

export const bookingService = {
  createBooking: async (
    data: {
      instructor_id: string;
      slot_ids: string[];
      location_description?: string;
      latitude?: number;
      longitude?: number;
    },
    token: string
  ): Promise<BookingPreview> => {
    const response = await httpClient.post<ApiBookingResource>("/bookings", data, {
      token,
    });
    
    // Fetch public instructors to map properly
    const instructors = await instructorService.getPublicInstructors();
    return mapApiBookingToPreview(response.data, instructors);
  },

  getMyBookings: async (token: string, status?: string): Promise<BookingPreview[]> => {
    const path = status ? `/bookings?status=${status}` : "/bookings";
    const response = await httpClient.get<ApiBookingResource[]>(path, { token });
    
    const list = response.data || [];
    const instructors = await instructorService.getPublicInstructors();
    
    return list.map((item) => mapApiBookingToPreview(item, instructors));
  },

  getBookingDetail: async (bookingId: string, token: string): Promise<ApiBookingResource> => {
    const response = await httpClient.get<ApiBookingResource>(`/bookings/${bookingId}`, {
      token,
    });
    return response.data;
  },

  confirmBooking: async (bookingId: string, token: string): Promise<ApiBookingResource> => {
    const response = await httpClient.patch<ApiBookingResource>(
      `/bookings/${bookingId}/confirm`,
      {},
      { token }
    );
    return response.data;
  },

  cancelBooking: async (
    bookingId: string,
    token: string,
    reason?: string
  ): Promise<ApiBookingResource> => {
    const response = await httpClient.patch<ApiBookingResource>(
      `/bookings/${bookingId}/cancel`,
      { reason },
      { token }
    );
    return response.data;
  },
};
