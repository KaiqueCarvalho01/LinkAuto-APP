import type { InstructorSummary } from "./instructor";

export type BookingStatus =
  | "PENDENTE"
  | "CONFIRMADA"
  | "REALIZADA"
  | "CANCELADA";

export type SlotState = "DISPONIVEL" | "RESERVADO" | "BLOQUEADO";

export interface BookingSlot {
  id: string;
  label: string;
  startAt: string;
  endAt: string;
  state: SlotState;
}

export interface BookingPreview {
  id: string;
  instructor: InstructorSummary;
  dateLabel: string;
  timeLabel: string;
  status: BookingStatus;
  cancellationReason?: string | undefined;
}

export interface BookingMessage {
  id: string;
  bookingId: string;
  senderId: string;
  content: string;
  createdAt: string;
}

export interface BookingReview {
  id: string;
  bookingId: string;
  reviewerId: string;
  reviewedId: string;
  rating: number;
  comment: string | null;
  createdAt: string;
}
