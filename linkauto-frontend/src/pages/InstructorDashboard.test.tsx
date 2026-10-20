import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import InstructorDashboard from "./InstructorDashboard";
import { adminService } from "../services/adminService";
import { httpClient } from "../services/httpClient";
import { renderWithProviders } from "../test/renderWithProviders";
import type { DashboardRequest } from "../types/session";

const REQUEST: DashboardRequest = {
	id: "inst-1",
	name: "Rafael Lima",
	city: "Campinas - SP",
	neighborhood: "",
	date: "Pendente",
	time: "Revisão",
};

describe("Admin approval screen", () => {
	afterEach(() => {
		vi.restoreAllMocks();
	});

	it("asks for a reason before rejecting and sends it", async () => {
		const user = userEvent.setup();
		const onReject = vi.fn();
		renderWithProviders(
			<InstructorDashboard requests={[REQUEST]} onReject={onReject} requireRejectReason />,
		);

		await user.click(screen.getByRole("button", { name: /recusar/i }));
		const confirm = screen.getByRole("button", { name: /confirmar recusa/i });
		expect(confirm).toBeDisabled();
		expect(onReject).not.toHaveBeenCalled();

		await user.type(
			screen.getByLabelText(/motivo da recusa/i),
			"  Credencial DETRAN vencida ",
		);
		await user.click(confirm);

		await waitFor(() => {
			expect(onReject).toHaveBeenCalledWith("inst-1", "Credencial DETRAN vencida");
		});
	});

	it("shows the city, the total pending and the last error", () => {
		renderWithProviders(
			<InstructorDashboard
				requests={[REQUEST]}
				pendingTotal={37}
				actionError="Não foi possível aprovar o instrutor. Tente novamente."
			/>,
		);

		// An empty neighborhood no longer hides the city
		expect(screen.getByText("Campinas - SP")).toBeInTheDocument();
		expect(screen.getByText("37 PENDENTES")).toBeInTheDocument();
		expect(screen.getByRole("alert")).toHaveTextContent("Não foi possível aprovar");
	});

	it("rejects right away when no reason is required (instructor answering a booking)", async () => {
		const user = userEvent.setup();
		const onReject = vi.fn();
		renderWithProviders(<InstructorDashboard requests={[REQUEST]} onReject={onReject} />);

		await user.click(screen.getByRole("button", { name: /recusar/i }));

		expect(onReject).toHaveBeenCalledWith("inst-1", undefined);
		expect(screen.queryByLabelText(/motivo da recusa/i)).not.toBeInTheDocument();
	});

	it("has no buttons for features that don't exist yet", () => {
		renderWithProviders(<InstructorDashboard requests={[REQUEST]} />);

		expect(screen.queryByRole("button", { name: /meus alunos/i })).not.toBeInTheDocument();
		expect(screen.queryByRole("button", { name: /conquistas/i })).not.toBeInTheDocument();
	});
});

describe("adminService", () => {
	afterEach(() => {
		vi.restoreAllMocks();
	});

	it("loads every pending instructor with the real total", async () => {
		const getSpy = vi.spyOn(httpClient, "get").mockResolvedValue({
			data: [
				{
					id: "inst-1",
					email: "rafael@test.com",
					roles: ["INSTRUTOR"],
					is_active: true,
					student_profile: null,
					instructor_profile: { full_name: "Rafael Lima", city: "Campinas", state: "SP" },
					created_at: "",
					updated_at: "",
				},
			],
			meta: { pagination: { page: 1, page_size: 100, total: 137 } },
		} as never);

		const pending = await adminService.getPendingInstructors("t");

		expect(getSpy).toHaveBeenCalledWith(
			"/admin/instructors?status=PENDENTE&page_size=100",
			{ token: "t" },
		);
		expect(pending.total).toBe(137);
		expect(pending.requests[0]).toMatchObject({ name: "Rafael Lima", city: "Campinas - SP" });
	});

	it("sends the typed reason when rejecting", async () => {
		const patchSpy = vi.spyOn(httpClient, "patch").mockResolvedValue({} as never);

		await adminService.rejectInstructor("inst-1", "Credencial vencida", "t");

		expect(patchSpy).toHaveBeenCalledWith(
			"/admin/instructors/inst-1/reject",
			{ reason: "Credencial vencida" },
			{ token: "t" },
		);
	});
});
