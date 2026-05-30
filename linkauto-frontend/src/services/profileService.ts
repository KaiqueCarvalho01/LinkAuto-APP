import { httpClient } from "./httpClient";
import type { ApiUserAccount } from "../types/api.types";
import type { UserAccount } from "../types/session";

export const mapApiUserToSessionUser = (api: ApiUserAccount): UserAccount => {
  return {
    id: api.id,
    email: api.email,
    roles: api.roles,
    is_active: api.is_active,
    student_profile: api.student_profile
      ? {
          full_name: api.student_profile.full_name ?? "",
          phone: api.student_profile.phone ?? "",
          city: api.student_profile.city ?? "",
          state: api.student_profile.state ?? "",
          license_type: api.student_profile.license_type,
          avatar_url: api.student_profile.avatar_url ?? "",
        }
      : null,
    instructor_profile: api.instructor_profile
      ? {
          full_name: api.instructor_profile.full_name ?? "",
          phone: api.instructor_profile.phone ?? "",
          city: api.instructor_profile.city ?? "",
          state: api.instructor_profile.state ?? "",
          bio: api.instructor_profile.bio ?? "",
          specialties: api.instructor_profile.specialties,
          price_per_hour:
            typeof api.instructor_profile.price_per_hour === "string"
              ? parseFloat(api.instructor_profile.price_per_hour)
              : api.instructor_profile.price_per_hour ?? 0.0,
          avatar_url: api.instructor_profile.avatar_url ?? "",
          detran_status: api.instructor_profile.detran_status,
          action_radius_km: api.instructor_profile.action_radius_km,
          latitude: api.instructor_profile.latitude ?? undefined,
          longitude: api.instructor_profile.longitude ?? undefined,
          rating_avg: api.instructor_profile.rating_avg,
          rating_count: api.instructor_profile.rating_count,
          is_active: api.instructor_profile.is_active,
        }
      : null,
    created_at: api.created_at,
    updated_at: api.updated_at,
  };
};

export interface StudentProfileUpdateInput {
  fullName?: string | undefined;
  phone?: string | undefined;
  city?: string | undefined;
  state?: string | undefined;
  licenseType?: string | undefined;
  avatarUrl?: string | undefined;
}

export interface InstructorProfileUpdateInput {
  fullName?: string | undefined;
  phone?: string | undefined;
  city?: string | undefined;
  state?: string | undefined;
  bio?: string | undefined;
  specialties?: string[] | undefined;
  pricePerHour?: number | undefined;
  avatarUrl?: string | undefined;
  actionRadiusKm?: number | undefined;
  latitude?: number | undefined;
  longitude?: number | undefined;
  isActive?: boolean | undefined;
}

export const profileService = {
  getMyProfile: async (token: string): Promise<UserAccount> => {
    const response = await httpClient.get<ApiUserAccount>("/users/me", { token });
    return mapApiUserToSessionUser(response.data);
  },

  updateStudentProfile: async (
    data: StudentProfileUpdateInput,
    token: string
  ): Promise<UserAccount> => {
    // strict nesting using extra="forbid" backend rule
    const payload = {
      student_profile: {
        full_name: data.fullName,
        phone: data.phone,
        city: data.city,
        state: data.state,
        license_type: data.licenseType,
        avatar_url: data.avatarUrl,
      },
    };
    
    const response = await httpClient.patch<ApiUserAccount>("/users/me", payload, {
      token,
    });
    return mapApiUserToSessionUser(response.data);
  },

  updateInstructorProfile: async (
    data: InstructorProfileUpdateInput,
    token: string
  ): Promise<UserAccount> => {
    const payload = {
      instructor_profile: {
        full_name: data.fullName,
        phone: data.phone,
        city: data.city,
        state: data.state,
        bio: data.bio,
        specialties: data.specialties,
        price_per_hour: data.pricePerHour,
        avatar_url: data.avatarUrl,
        action_radius_km: data.actionRadiusKm,
        latitude: data.latitude,
        longitude: data.longitude,
        is_active: data.isActive,
      },
    };
    
    const response = await httpClient.patch<ApiUserAccount>("/users/me", payload, {
      token,
    });
    return mapApiUserToSessionUser(response.data);
  },
};
