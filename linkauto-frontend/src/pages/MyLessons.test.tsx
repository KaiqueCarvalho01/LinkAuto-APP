/* eslint-disable @typescript-eslint/no-explicit-any */
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import MyLessons from "./MyLessons";
import { mockBookings } from "../test/fixtures/mockData";
import { renderWithProviders } from "../test/renderWithProviders";
import { bookingService } from "../services/bookingService";

describe("MyLessons - Cancelamento", () => {
	it("exibe confirmacao inline ao tentar cancelar aula e executa com sucesso", async () => {
		const onNewBooking = vi.fn();
		const user = userEvent.setup();

		// Mock da lista de bookings inicial e após cancelamento
		const initialBookings = [
			{ ...mockBookings[0], id: "booking-1", status: "PENDENTE" as const },
		] as any[];
		vi.spyOn(bookingService, "getMyBookings").mockResolvedValueOnce(initialBookings).mockResolvedValueOnce([]);
		const cancelSpy = vi.spyOn(bookingService, "cancelBooking").mockResolvedValue({} as any);

		renderWithProviders(
			<MyLessons token="mock-token" onNewBooking={onNewBooking} />
		);

		// Espera os bookings carregarem
		const cancelBtn = await screen.findByRole("button", { name: /cancelar aula/i });
		expect(cancelBtn).toBeInTheDocument();

		// Clica em Cancelar Aula
		await user.click(cancelBtn);

		// O botão original de cancelar some e aparecem as opções de confirmação inline
		expect(cancelBtn).not.toBeInTheDocument();

		const confirmBtn = screen.getByRole("button", { name: /sim, cancelar/i });
		const noBtn = screen.getByRole("button", { name: /não/i });
		expect(confirmBtn).toBeInTheDocument();
		expect(noBtn).toBeInTheDocument();

		// Clica em "Sim, cancelar"
		await user.click(confirmBtn);

		// Valida se o cancelBooking foi chamado com os argumentos corretos
		await waitFor(() => {
			expect(cancelSpy).toHaveBeenCalledWith("booking-1", "mock-token", "Cancelado pelo Aluno");
		});

		// Deve recarregar a lista (e como o segundo mockResolvedValueOnce retorna lista vazia, exibe mensagem de lista vazia)
		await screen.findByText(/nenhum agendamento encontrado/i);
	});

	it("mostra erro na tela se o cancelamento falhar e permite tentar novamente", async () => {
		const onNewBooking = vi.fn();
		const user = userEvent.setup();

		const initialBookings = [
			{ ...mockBookings[0], id: "booking-2", status: "PENDENTE" as const },
		] as any[];
		vi.spyOn(bookingService, "getMyBookings").mockResolvedValue(initialBookings);
		vi.spyOn(bookingService, "cancelBooking").mockRejectedValue(new Error("Erro de rede no cancelamento"));

		renderWithProviders(
			<MyLessons token="mock-token" onNewBooking={onNewBooking} />
		);

		const cancelBtn = await screen.findByRole("button", { name: /cancelar aula/i });
		await user.click(cancelBtn);

		const confirmBtn = screen.getByRole("button", { name: /sim, cancelar/i });
		await user.click(confirmBtn);

		// Espera a mensagem de erro aparecer na tela
		await screen.findByText("Erro de rede no cancelamento");

		// O botão "Sim, cancelar" deve continuar na tela e não estar em loading após a falha
		expect(screen.getByRole("button", { name: /sim, cancelar/i })).toBeInTheDocument();
		expect(screen.getByRole("button", { name: /sim, cancelar/i })).not.toBeDisabled();
	});
});
