import { useCallback, useEffect, useState } from "react";
import { Search, MapPin } from "lucide-react";
import {
  Box,
  Button,
  chakra,
  Container,
  Grid,
  Heading,
  Input,
  SimpleGrid,
  Skeleton,
  Stack,
  Text,
} from "@chakra-ui/react";

import { InstructorCard } from "../components/InstructorCard";
import { InstructorMap } from "../components/InstructorMap";
import { instructorService } from "../services/instructorService";
import type {
  InstructorSearchParams,
  InstructorSummary,
} from "../types/instructor";

interface SearchPageProps {
  readonly token: string | undefined;
  readonly onOpenProfile: () => void;
  readonly onStartBooking: (instructor: InstructorSummary) => void;
}

const citiesCoords: Record<string, { lat: number; lng: number }> = {
  "Mogi Mirim": { lat: -22.4319, lng: -46.9578 },
  "Mogi Guaçu": { lat: -22.3708, lng: -46.9428 },
  "Estiva Gerbi": { lat: -22.2842, lng: -46.9692 },
};

const specialties = ["Todas", "Carro", "Moto", "Medo de Dirigir", "Habilitação PCD"];

export default function SearchPage({
  token,
  onOpenProfile,
  onStartBooking,
}: SearchPageProps) {
  const [selectedCity, setSelectedCity] = useState("Mogi Mirim");
  const [coords, setCoords] = useState<{ lat: number; lng: number }>({
    lat: -22.4319,
    lng: -46.9578,
  });
  const [specialty, setSpecialty] = useState("Todas");
  const [radiusKm, setRadiusKm] = useState(10);
  const minRating = 0;
  const [maxPrice, setMaxPrice] = useState("");
  const [loading, setLoading] = useState(false);
  const [instructors, setInstructors] = useState<InstructorSummary[]>([]);
  const [selectedInstructorId, setSelectedInstructorId] = useState<string>();
  const [geoStatus, setGeoStatus] = useState<"idle" | "loading" | "success" | "error">("idle");

  const handleCityChange = (cityName: string) => {
    setSelectedCity(cityName);
    if (citiesCoords[cityName]) {
      setCoords(citiesCoords[cityName]);
      setGeoStatus("idle");
    }
  };

  const handleGetLocation = () => {
    if (!navigator.geolocation) {
      alert("Geolocalização não é suportada pelo seu navegador.");
      return;
    }

    setGeoStatus("loading");
    navigator.geolocation.getCurrentPosition(
      (position) => {
        setCoords({
          lat: position.coords.latitude,
          lng: position.coords.longitude,
        });
        setSelectedCity("Localização Atual");
        setGeoStatus("success");
      },
      (error) => {
        console.error("Error getting location:", error);
        setGeoStatus("error");
        alert("Não foi possível obter sua localização. Usando Mogi Mirim como padrão.");
        setCoords(citiesCoords["Mogi Mirim"] ?? { lat: -22.4319, lng: -46.9578 });
        setSelectedCity("Mogi Mirim");
      }
    );
  };

  const loadInstructors = useCallback(async () => {
    setLoading(true);
    const params: InstructorSearchParams = {
      latitude: coords.lat,
      longitude: coords.lng,
      radiusKm,
      specialty,
      minRating: minRating > 0 ? minRating : undefined,
      maxPrice: maxPrice.trim() !== "" ? parseFloat(maxPrice) : undefined,
    };

    try {
      const results = await instructorService.searchInstructors(params, token);
      setInstructors(results);
      setSelectedInstructorId((current) => current ?? results[0]?.id);
    } catch (err) {
      console.error("Error searching instructors:", err);
      setInstructors([]);
    } finally {
      setLoading(false);
    }
  }, [coords, radiusKm, specialty, minRating, maxPrice, token]);

  useEffect(() => {
    void loadInstructors();
  }, [loadInstructors]);

  const selectedInstructor =
    instructors.find((item) => item.id === selectedInstructorId) ??
    instructors[0] ??
    null;

  return (
    <Stack minH="100vh" pb={10}>
      <Container maxW="7xl" pt={8}>
        <Stack gap={6}>
          <Stack gap={1.5}>
            <Heading
              fontSize={{ base: "2xl", md: "3xl" }}
              color="text.primary">
              Buscar instrutores disponíveis
            </Heading>
            <Text color="text.muted" maxW="760px">
              Encontre instrutores aprovados, compare avaliação e
              selecione slots para iniciar seu agendamento de
              forma segura.
            </Text>
          </Stack>

          <SimpleGrid columns={{ base: 1, md: 2, lg: 6 }} gap={3} alignItems="center">
            {/* City Dropdown */}
            <Box>
              <chakra.select
                value={selectedCity}
                onChange={(event) => handleCityChange(event.target.value)}
                h="46px"
                w="100%"
                borderRadius="md"
                border="1px solid"
                borderColor="border.default"
                bg="surface.panel"
                px={3}
                fontSize="sm"
                fontWeight="600"
                color="text.primary"
                aria-label="Cidade">
                {Object.keys(citiesCoords).map((cityOption) => (
                  <option key={cityOption} value={cityOption}>
                    {cityOption}
                  </option>
                ))}
                {selectedCity === "Localização Atual" && (
                  <option value="Localização Atual">Localização Atual</option>
                )}
              </chakra.select>
            </Box>

            {/* Geolocation Button */}
            <Button
              onClick={handleGetLocation}
              h="46px"
              variant="outline"
              borderColor="border.default"
              bg="surface.panel"
              color="text.primary"
              loading={geoStatus === "loading"}
              _hover={{ bg: "surface.muted" }}>
              <MapPin size={16} />
              GPS
            </Button>

            {/* Specialty Filter */}
            <chakra.select
              value={specialty}
              onChange={(event) => setSpecialty(event.target.value)}
              h="46px"
              borderRadius="md"
              border="1px solid"
              borderColor="border.default"
              bg="surface.panel"
              px={3}
              fontSize="sm"
              fontWeight="600"
              color="text.primary"
              aria-label="Especialidade">
              {specialties.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </chakra.select>

            {/* Radius Filter */}
            <chakra.select
              value={radiusKm}
              onChange={(event) => setRadiusKm(parseInt(event.target.value, 10))}
              h="46px"
              borderRadius="md"
              border="1px solid"
              borderColor="border.default"
              bg="surface.panel"
              px={3}
              fontSize="sm"
              fontWeight="600"
              color="text.primary"
              aria-label="Raio de Busca (km)">
              <option value="5">Até 5 km</option>
              <option value="10">Até 10 km</option>
              <option value="15">Até 15 km</option>
              <option value="20">Até 20 km</option>
              <option value="50">Até 50 km</option>
            </chakra.select>

            {/* Price Max Filter */}
            <Input
              placeholder="Preço máx. (R$/h)"
              type="number"
              min={0}
              value={maxPrice}
              onChange={(event) => setMaxPrice(event.target.value)}
              h="46px"
              bg="surface.panel"
              borderColor="border.default"
              color="text.primary"
            />

            {/* Search Trigger Button */}
            <Button
              h="46px"
              bg="brand.solid"
              color="text.inverse"
              onClick={() => {
                void loadInstructors();
              }}
              loading={loading}
              _hover={{ bg: "brand.emphasized" }}>
              <Search size={16} />
              Buscar
            </Button>
          </SimpleGrid>

          <Grid
            templateColumns={{ base: "1fr", lg: "1.05fr 0.95fr" }}
            gap={4}>
            <Stack gap={3.5}>
              {loading
                ? [
                    "skeleton-card-1",
                    "skeleton-card-2",
                    "skeleton-card-3",
                  ].map((key) => (
                    <Skeleton
                      key={key}
                      h="180px"
                      borderRadius="2xl"
                    />
                  ))
                : null}

              {!loading && instructors.length === 0 ? (
                <Box
                  py={16}
                  px={6}
                  textAlign="center"
                  bg="surface.panel"
                  border="1px dashed"
                  borderColor="border.default"
                  borderRadius="2xl">
                  <Text
                    fontWeight="700"
                    color="text.secondary">
                    Nenhum instrutor encontrado com este
                    filtro.
                  </Text>
                  <Text
                    mt={1.5}
                    color="text.muted"
                    fontSize="sm">
                    Tente aumentar o raio de busca ou
                    remover filtros.
                  </Text>
                </Box>
              ) : null}

              {loading
                ? null
                : instructors.map((instructor) => (
                    <InstructorCard
                      key={instructor.id}
                      instructor={instructor}
                      selected={
                        instructor.id ===
                        selectedInstructor?.id
                      }
                      onOpenProfile={() =>
                        onOpenProfile()
                      }
                      onBook={onStartBooking}
                    />
                  ))}
            </Stack>

            <InstructorMap
              instructors={instructors}
              selectedInstructorId={selectedInstructor?.id}
              onSelect={setSelectedInstructorId}
              onBook={onStartBooking}
            />
          </Grid>
        </Stack>
      </Container>
    </Stack>
  );
}
