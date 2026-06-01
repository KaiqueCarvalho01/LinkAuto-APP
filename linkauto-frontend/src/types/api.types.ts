export interface ApiStudentProfile {
  full_name: string | null;
  phone: string | null;
  city: string | null;
  state: string | null;
  license_type: string;
  avatar_url: string | null;
}

export interface ApiInstructorProfile {
  full_name: string | null;
  phone: string | null;
  city: string | null;
  state: string | null;
  bio: string | null;
  specialties: string[];
  price_per_hour: number | string | null;
  avatar_url: string | null;
  detran_status: string;
  action_radius_km: number;
  latitude: number | null;
  longitude: number | null;
  rating_avg: number;
  rating_count: number;
  is_active: boolean;
}

export interface ApiUserAccount {
  id: string;
  email: string;
  roles: string[];
  is_active: boolean;
  student_profile: ApiStudentProfile | null;
  instructor_profile: ApiInstructorProfile | null;
  created_at: string;
  updated_at: string;
}

export interface ApiInstructorSearchResult {
  user_id: string;
  full_name: string;
  city: string;
  state: string;
  specialties: string[];
  price_per_hour: number | null;
  rating_avg: number;
  rating_count: number;
  latitude: number;
  longitude: number;
  action_radius_km: number;
}

export interface ApiSlotResource {
  id: string;
  instructor_id: string;
  starts_at: string;
  ends_at: string;
  status: string;
}

export interface ApiBookingSlotResource {
  id: string;
  booking_id: string;
  slot_id: string;
  slot: ApiSlotResource;
}

export interface ApiBookingResource {
  id: string;
  student_id: string;
  instructor_id: string;
  status: string;
  location_description: string | null;
  latitude: number | null;
  longitude: number | null;
  created_at: string;
  confirmed_at: string | null;
  cancelled_at: string | null;
  cancelled_by: string | null;
  cancellation_reason: string | null;
  slots: ApiBookingSlotResource[];
}

export interface ApiMessageResource {
  id: string;
  booking_id: string;
  sender_id: string;
  content: string;
  created_at: string;
}

export interface ApiReviewResource {
  id: string;
  booking_id: string;
  reviewer_id: string;
  reviewed_id: string;
  rating: number;
  comment: string | null;
  created_at: string;
  updated_at: string;
}
