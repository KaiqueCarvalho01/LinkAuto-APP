export type UserRole = "ALUNO" | "INSTRUTOR" | "ADMIN";

export interface StudentProfile {
	full_name?: string;
	city?: string;
	license_type?: string;
	[key: string]: unknown;
}

export interface InstructorProfile {
	full_name?: string;
	city?: string;
	detran_status?: string;
	bio?: string;
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
}
