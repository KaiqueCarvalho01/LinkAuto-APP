import { httpClient } from "./httpClient";
import type { DashboardRequest, UserAccount } from "../types/session";

// The API's maximum page size: admins see every pending request, not just the first 20
const PENDING_PAGE_SIZE = 100;

export interface PendingInstructors {
	readonly requests: DashboardRequest[];
	readonly total: number;
}

const toRequest = (account: UserAccount): DashboardRequest => {
	const profile = account.instructor_profile;
	const place = [profile?.city, profile?.state].filter(Boolean).join(" - ");
	return {
		id: account.id,
		name: profile?.full_name || account.email,
		city: place || "Sem cidade",
		date: "Pendente",
		time: "Revisão",
		specialties: profile?.specialties || [],
	};
};

export const adminService = {
	getPendingInstructors: async (token: string): Promise<PendingInstructors> => {
		const response = await httpClient.get<UserAccount[]>(
			`/admin/instructors?status=PENDENTE&page_size=${PENDING_PAGE_SIZE}`,
			{ token },
		);
		const accounts = response.data || [];
		const pagination = response.meta?.pagination as { total?: number } | undefined;
		return {
			requests: accounts.map(toRequest),
			total: pagination?.total ?? accounts.length,
		};
	},

	approveInstructor: async (instructorId: string, token: string): Promise<void> => {
		await httpClient.patch(`/admin/instructors/${instructorId}/approve`, {}, { token });
	},

	// The reason is e-mailed to the instructor
	rejectInstructor: async (instructorId: string, reason: string, token: string): Promise<void> => {
		await httpClient.patch(`/admin/instructors/${instructorId}/reject`, { reason }, { token });
	},
};
