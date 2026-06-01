export type UserRole = "ALUNO" | "INSTRUTOR" | "ADMIN";

export interface StudentProfile {
	full_name?: string;
	phone?: string;
	city?: string;
	state?: string;
	license_type?: string;
	avatar_url?: string;
	[key: string]: unknown;
}

export interface InstructorProfile {
	full_name?: string;
	phone?: string;
	city?: string;
	state?: string;
	neighborhood?: string;
	detran_status?: string;
	bio?: string;
	specialties?: string[];
	price_per_hour?: number;
	avatar_url?: string;
	action_radius_km?: number;
	latitude?: number | undefined;
	longitude?: number | undefined;
	rating_avg?: number;
	rating_count?: number;
	is_active?: boolean;
	[key: string]: unknown;
}

export interface UserAccount {
	id: string;
	email: string;
	roles: string[];
	is_active: boolean;
	student_profile: StudentProfile | null;
	instructor_profile: InstructorProfile | null;
	created_at: string;
	updated_at: string;
}

export interface SessionData {
	accessToken: string;
	tokenType: string;
	user: UserAccount;
}

export interface AuthLoginResponse {
	access_token: string;
	token_type: string;
	expires_in: number;
}

export interface SignInInput {
	email: string;
	password: string;
}

export type UiRole = "student" | "instructor" | "admin";

export interface ProfileUserData {
	name: string;
	email: string;
	role: UiRole;
}

export interface DashboardRequest {
	id: string;
	name: string;
	city: string;
	date: string;
	time: string;
	studentName?: string;
	neighborhood?: string;
	specialties?: string[];
}
