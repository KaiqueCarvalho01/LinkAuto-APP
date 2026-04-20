import { expect, test, type APIRequestContext } from "@playwright/test";

const apiBaseUrl =
	process.env.E2E_API_BASE_URL ?? "http://127.0.0.1:8000/api/v1";

const studentPassword = "SenhaForte123";

const createStudentUser = async (
	request: APIRequestContext,
	email: string,
): Promise<void> => {
	const register = await request.post(`${apiBaseUrl}/auth/register`, {
		data: {
			email,
			password: studentPassword,
			roles: ["ALUNO"],
		},
	});

	expect(register.ok()).toBeTruthy();
};

test.describe("Student booking smoke", () => {
	test("logs in and completes booking request flow", async ({
		page,
		request,
	}) => {
		const email = `e2e.student.${Date.now()}@linkauto.app`;
		await createStudentUser(request, email);

		await page.goto("/login");

		await test.step("Authenticate in login form", async () => {
			await page.getByLabel("E-mail").fill(email);
			await page.getByLabel("Senha").fill(studentPassword);
			await page
				.getByRole("button", { name: "Entrar no LinkAuto" })
				.click();
			await expect(page).toHaveURL(/\/buscar$/);
		});

		await test.step("Open lesson details from search list", async () => {
			await expect(
				page.getByRole("heading", {
					name: "Buscar instrutores disponiveis",
				}),
			).toHaveCount(1);
			await page.getByRole("button", { name: "Agendar" }).first().click();
			await expect(page).toHaveURL(/\/bookings\/new$/);
		});

		await test.step("Select two consecutive slots and submit", async () => {
			const submit = page.getByRole("button", {
				name: "Solicitar agendamento",
			});
			await expect(submit).toBeDisabled();

			await page.getByTestId(/slot-.*-slot-0/).click();
			await expect(submit).toBeDisabled();

			await page.getByTestId(/slot-.*-slot-1/).click();
			await expect(submit).toBeEnabled();

			await submit.click();
			await expect(page).toHaveURL(/\/agendamentos$/);
			await expect(
				page.getByRole("heading", { name: "Meus agendamentos" }),
			).toHaveCount(1);
		});
	});
});
