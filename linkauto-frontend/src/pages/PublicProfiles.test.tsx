import { render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { ChakraProvider, defaultSystem } from "@chakra-ui/react";

import InstructorPublicProfilePage from "./InstructorPublicProfilePage";
import StudentPublicProfilePage from "./StudentPublicProfilePage";
import { profileService } from "../services/profileService";

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

  it("renders public instructor profile with details, CTA button, and reviews (without slots)", async () => {
    vi.mocked(profileService.fetchPublicInstructorProfile).mockResolvedValueOnce({
      id: "marcos-lima-mogi-mirim-4a9b",
      slug: "marcos-lima-mogi-mirim-4a9b",
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
            id: "camila-rocha-mogi-mirim-7e2a",
            slug: "camila-rocha-mogi-mirim-7e2a",
            full_name: "Camila Rocha",
          },
        },
      ],
    });

    renderWithProviders(
      <MemoryRouter initialEntries={["/instructors/marcos-lima-mogi-mirim-4a9b"]}>
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
    expect(screen.getByText("Agendar Aula com este Instrutor")).toBeInTheDocument();
  });

  it("renders friendly error state when instructor slug is not found", async () => {
    vi.mocked(profileService.fetchPublicInstructorProfile).mockRejectedValueOnce(
      new Error("Not found")
    );

    renderWithProviders(
      <MemoryRouter initialEntries={["/instructors/non-existent-slug"]}>
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

  it("renders public student profile with stats and instructor reviews with public slugs", async () => {
    vi.mocked(profileService.fetchPublicStudentProfile).mockResolvedValueOnce({
      id: "mariana-souza-mogi-mirim-1c2d",
      slug: "mariana-souza-mogi-mirim-1c2d",
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
            id: "carlos-instrutor-mogi-mirim-9b3f",
            slug: "carlos-instrutor-mogi-mirim-9b3f",
            full_name: "Carlos Instrutor",
          },
        },
      ],
    });

    renderWithProviders(
      <MemoryRouter initialEntries={["/students/mariana-souza-mogi-mirim-1c2d"]}>
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
