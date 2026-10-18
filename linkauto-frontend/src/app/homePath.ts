export type PreferredRole = "student" | "instructor";

// Where a signed-in user lands: admins on their panel, instructors on their dashboard
// (unless they signed in as a student and have that role), students on the search
export const homePathFor = (roles: string[], preferredRole?: PreferredRole): string => {
	if (roles.includes("ADMIN")) return "/admin/instructors";
	const isStudent = roles.includes("ALUNO");
	const isInstructor = roles.includes("INSTRUTOR");
	if (isStudent && (preferredRole === "student" || !isInstructor)) return "/search";
	if (isInstructor) return "/instructor/dashboard";
	return "/profile";
};
