import { render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { ChakraProvider, defaultSystem } from "@chakra-ui/react";

import InstructorPublicProfilePage from "./InstructorPublicProfilePage";
import StudentPublicProfilePage from "./StudentPublicProfilePage";
import { profileService } from "../services/profileService";
import { slotService } from "../services/slotService";

vi.mock("../state/sessionStore", () => ({
  useSessionStore: () => ({
    isAuthenticated: false,
    roles: [],
    session: null,
  }),
}));

vi.mock("../services/profileService", () => ({
  profileService: {
    fetchPublicInstructorProfile: vi.fn(),
    fetchPublicStudentProfile: vi.fn(),
  },
}));

vi.mock("../services/slotService", () => ({
  slotService: {
    getInstructorSlots: vi.fn(),
  },
}));

function renderWithProviders(ui: React.ReactElement) {
  return render(
    <ChakraProvider value={defaultSystem}>
      {ui}
    </ChakraProvider>
  );
}

describe("InstructorPublicProfilePage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders public instructor profile with details, slots, and reviews", async () => {
    vi.mocked(profileService.fetchPublicInstructorProfile).mockResolvedValueOnce({
      id: "inst-1",
      full_name: "Marcos Lima",
      city: "Mogi Mirim",
      state: "SP",
      bio: "Especialista em alunos com fobia de volante.",
      specialties: ["Baliza", "Medo de Dirigir"],
      price_per_hour: 90,
      rating_avg: 4.9,
      rating_count: 8,
      detran_approved: true,
      reviews: [
        {
          id: "rev-1",
          rating: 5,
          comment: "Excelente paciência e didática!",
          created_at: "2026-08-20T10:00:00Z",
          reviewer: {
            id: "stud-1",
            full_name: "Camila Rocha",
          },
        },
      ],
    });

    vi.mocked(slotService.getInstructorSlots).mockResolvedValueOnce([
      {
        id: "slot-1",
        label: "08:00 - 09:00",
        startAt: "2026-08-25T08:00:00Z",
        endAt: "2026-08-25T09:00:00Z",
        state: "DISPONIVEL",
      },
      {
        id: "slot-2",
        label: "09:00 - 10:00",
        startAt: "2026-08-25T09:00:00Z",
        endAt: "2026-08-25T10:00:00Z",
        state: "DISPONIVEL",
      },
    ]);

    renderWithProviders(
      <MemoryRouter initialEntries={["/instructors/inst-1"]}>
        <Routes>
          <Route path="/instructors/:id" element={<InstructorPublicProfilePage />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText("Marcos Lima")).toBeInTheDocument();
    });

    expect(screen.getByText("DETRAN Validado")).toBeInTheDocument();
    expect(screen.getByText("Mogi Mirim, SP")).toBeInTheDocument();
    expect(screen.getByText("Baliza")).toBeInTheDocument();
    expect(screen.getByText("Medo de Dirigir")).toBeInTheDocument();
    expect(screen.getByText("Especialista em alunos com fobia de volante.")).toBeInTheDocument();
    expect(screen.getByText("Camila Rocha")).toBeInTheDocument();
    expect(screen.getByText(/"Excelente paciência e didática!"/)).toBeInTheDocument();
    expect(screen.getByText("08:00 - 09:00")).toBeInTheDocument();
  });

  it("renders friendly error state when instructor is not found", async () => {
    vi.mocked(profileService.fetchPublicInstructorProfile).mockRejectedValueOnce(
      new Error("Not found")
    );
    vi.mocked(slotService.getInstructorSlots).mockResolvedValueOnce([]);

    renderWithProviders(
      <MemoryRouter initialEntries={["/instructors/non-existent"]}>
        <Routes>
          <Route path="/instructors/:id" element={<InstructorPublicProfilePage />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText("Perfil Indisponível")).toBeInTheDocument();
    });
    expect(screen.getByText("Voltar para a Busca")).toBeInTheDocument();
  });
});

describe("StudentPublicProfilePage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders public student profile with stats and instructor reviews", async () => {
    vi.mocked(profileService.fetchPublicStudentProfile).mockResolvedValueOnce({
      id: "stud-1",
      full_name: "Mariana Souza",
      city: "Mogi Mirim",
      state: "SP",
      license_type: "EM_PROCESSO",
      rating_avg: 5.0,
      rating_count: 3,
      completed_lessons_count: 6,
      reviews: [
        {
          id: "rev-2",
          rating: 5,
          comment: "Aluna muito atenta às regras de trânsito.",
          created_at: "2026-08-21T14:00:00Z",
          reviewer: {
            id: "inst-1",
            full_name: "Carlos Instrutor",
          },
        },
      ],
    });

    renderWithProviders(
      <MemoryRouter initialEntries={["/students/stud-1"]}>
        <Routes>
          <Route path="/students/:id" element={<StudentPublicProfilePage />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText("Mariana Souza")).toBeInTheDocument();
    });

    expect(screen.getByText("Primeira Habilitação (CNH)")).toBeInTheDocument();
    expect(screen.getByText("Mogi Mirim, SP")).toBeInTheDocument();
    expect(screen.getByText("6")).toBeInTheDocument();
    expect(screen.getByText("Carlos Instrutor")).toBeInTheDocument();
    expect(screen.getByText(/"Aluna muito atenta às regras de trânsito."/)).toBeInTheDocument();
  });
});
