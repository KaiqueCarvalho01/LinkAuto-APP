import { useEffect, useState } from "react";
import { useNavigate, useParams, Link as RouterLink } from "react-router-dom";
import {
  ArrowLeft,
  Calendar,
  CheckCircle2,
  MapPin,
  MessageSquare,
  ShieldCheck,
  Star,
  User,
} from "lucide-react";
import {
  Badge,
  Box,
  Button,
  Container,
  Heading,
  HStack,
  SimpleGrid,
  Skeleton,
  Stack,
  Text,
  VStack,
} from "@chakra-ui/react";

import { RatingStars } from "../components/RatingStars";
import { profileService } from "../services/profileService";
import { useSessionStore } from "../state/sessionStore";
import type { ApiPublicInstructorProfile } from "../types/api.types";
import type { InstructorSummary } from "../types/instructor";

const initialsFromName = (name: string): string => {
  const parts = name
    .trim()
    .split(" ")
    .filter((part) => part.length > 0)
    .slice(0, 2);
  return parts.map((part) => part[0]?.toUpperCase() ?? "").join("");
};

export default function InstructorPublicProfilePage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { isAuthenticated } = useSessionStore();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [instructor, setInstructor] = useState<ApiPublicInstructorProfile | null>(null);

  useEffect(() => {
    if (!id) {
      setError("Instrutor não especificado.");
      setLoading(false);
      return;
    }

    let isMounted = true;
    setLoading(true);
    setError(null);

    profileService.fetchPublicInstructorProfile(id)
      .then((prof) => {
        if (isMounted) {
          setInstructor(prof);
        }
      })
      .catch((err) => {
        console.error("Error loading public instructor profile:", err);
        if (isMounted) {
          setError("Instrutor não encontrado ou cadastro indisponível.");
        }
      })
      .finally(() => {
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [id]);

  const handleStartBooking = () => {
    if (!instructor) return;

    const summary: InstructorSummary = {
      id: instructor.id,
      slug: instructor.slug,
      fullName: instructor.full_name,
      city: instructor.city ?? "Mogi Mirim",
      neighborhood: instructor.state ?? "SP",
      rating: instructor.rating_avg,
      reviewsCount: instructor.rating_count,
      distanceKm: 0,
      hourlyRate: instructor.price_per_hour ?? 70,
      detranApproved: instructor.detran_approved,
      specialties: instructor.specialties,
      radiusKm: 15,
      coordinates: { lat: -22.4319, lng: -46.9578 },
    };

    if (!isAuthenticated) {
      navigate("/login", {
        state: {
          returnUrl: `/bookings/new`,
          instructor: summary,
        },
      });
      return;
    }

    navigate("/bookings/new", { state: { instructor: summary } });
  };

  if (loading) {
    return (
      <Container maxW="5xl" py={8}>
        <Stack gap={6}>
          <Skeleton h="40px" w="150px" borderRadius="md" />
          <Skeleton h="220px" borderRadius="2xl" />
          <Skeleton h="180px" borderRadius="2xl" />
          <Skeleton h="200px" borderRadius="2xl" />
        </Stack>
      </Container>
    );
  }

  if (error || !instructor) {
    return (
      <Container maxW="3xl" py={16} textAlign="center">
        <VStack gap={4} bg="surface.panel" p={8} borderRadius="2xl" border="1px solid" borderColor="border.default">
          <Box p={4} borderRadius="full" bg="surface.muted" color="text.muted">
            <User size={48} />
          </Box>
          <Heading size="lg" color="text.primary">
            Perfil Indisponível
          </Heading>
          <Text color="text.secondary">
            {error || "Não foi possível encontrar as informações deste instrutor."}
          </Text>
          <Button
            mt={4}
            variant="outline"
            onClick={() => navigate("/search")}>
            <ArrowLeft size={16} />
            Voltar para a Busca
          </Button>
        </VStack>
      </Container>
    );
  }

  return (
    <Container maxW="5xl" py={8}>
      <Stack gap={6}>
        {/* Back Link */}
        <Box>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate(-1)}
            color="text.secondary"
            _hover={{ bg: "surface.muted" }}>
            <ArrowLeft size={16} />
            Voltar
          </Button>
        </Box>

        {/* Profile Card Header */}
        <Box
          bg="surface.panel"
          p={{ base: 6, md: 8 }}
          borderRadius="2xl"
          border="1px solid"
          borderColor="border.default"
          boxShadow="sm">
          <Stack
            direction={{ base: "column", md: "row" }}
            justify="space-between"
            align={{ base: "start", md: "center" }}
            gap={6}>
            <HStack align="center" gap={5}>
              <Box
                w={{ base: "72px", md: "88px" }}
                h={{ base: "72px", md: "88px" }}
                borderRadius="full"
                display="grid"
                placeItems="center"
                bg="laBlue.100"
                color="laBlue.700"
                fontSize={{ base: "xl", md: "2xl" }}
                fontWeight="900"
                border="3px solid"
                borderColor="laGreen.100"
                overflow="hidden"
                flexShrink={0}>
                {instructor.avatar_url ? (
                  <img
                    src={instructor.avatar_url}
                    alt={instructor.full_name}
                    style={{ width: "100%", height: "100%", objectFit: "cover" }}
                  />
                ) : (
                  initialsFromName(instructor.full_name)
                )}
              </Box>

              <Stack gap={1.5}>
                <HStack gap={2} flexWrap="wrap" align="center">
                  <Heading size={{ base: "lg", md: "xl" }} color="text.primary">
                    {instructor.full_name}
                  </Heading>
                  {instructor.detran_approved && (
                    <Badge
                      px={2.5}
                      py={1}
                      borderRadius="full"
                      bg="laGreen.100"
                      color="laGreen.700"
                      fontWeight="700"
                      fontSize="xs"
                      display="inline-flex"
                      alignItems="center"
                      gap={1.5}>
                      <CheckCircle2 size={13} aria-hidden="true" />
                      DETRAN Validado
                    </Badge>
                  )}
                </HStack>

                <HStack gap={3} flexWrap="wrap" color="text.secondary" fontSize="sm">
                  {instructor.city && (
                    <HStack gap={1}>
                      <MapPin size={15} />
                      <Text fontWeight="500">
                        {instructor.city}{instructor.state ? `, ${instructor.state}` : ""}
                      </Text>
                    </HStack>
                  )}
                  <RatingStars
                    rating={instructor.rating_avg}
                    reviewsCount={instructor.rating_count}
                  />
                </HStack>
              </Stack>
            </HStack>

            <HStack gap={4} align="center" flexWrap="wrap">
              {instructor.price_per_hour !== null && instructor.price_per_hour !== undefined && (
                <Box
                  bg="surface.muted"
                  px={5}
                  py={3}
                  borderRadius="xl"
                  border="1px solid"
                  borderColor="border.default"
                  textAlign={{ base: "left", md: "right" }}>
                  <Text fontSize="xs" color="text.muted" textTransform="uppercase" fontWeight="700">
                    Valor da hora/aula
                  </Text>
                  <Text fontSize="2xl" fontWeight="900" color="brand.solid">
                    R$ {instructor.price_per_hour.toFixed(2)}
                    <Text as="span" fontSize="sm" color="text.secondary" fontWeight="600">
                      /h
                    </Text>
                  </Text>
                </Box>
              )}

              <Button
                bg="brand.solid"
                color="text.inverse"
                fontWeight="700"
                size="lg"
                onClick={handleStartBooking}
                _hover={{ bg: "brand.emphasized" }}>
                <Calendar size={18} />
                Agendar Aula
              </Button>
            </HStack>
          </Stack>
        </Box>

        {/* Bio and Specialties */}
        <SimpleGrid columns={{ base: 1, md: 3 }} gap={6}>
          <Box
            gridColumn={{ base: "span 1", md: "span 2" }}
            bg="surface.panel"
            p={6}
            borderRadius="2xl"
            border="1px solid"
            borderColor="border.default">
            <Heading size="md" mb={4} color="text.primary">
              Sobre o Instrutor
            </Heading>
            <Text color="text.secondary" fontSize="sm" lineHeight="tall">
              {instructor.bio || "Este instrutor ainda não adicionou uma biografia detalhada."}
            </Text>

            {instructor.specialties && instructor.specialties.length > 0 && (
              <Box mt={6}>
                <Text fontSize="xs" color="text.muted" textTransform="uppercase" fontWeight="700" mb={3}>
                  Especialidades e Habilidades
                </Text>
                <HStack gap={2} flexWrap="wrap">
                  {instructor.specialties.map((spec) => (
                    <Badge
                      key={spec}
                      px={3}
                      py={1.5}
                      bg="laBlue.100"
                      color="laBlue.700"
                      borderRadius="full"
                      fontWeight="600"
                      fontSize="xs">
                      {spec}
                    </Badge>
                  ))}
                </HStack>
              </Box>
            )}
          </Box>

          <Box
            bg="surface.panel"
            p={6}
            borderRadius="2xl"
            border="1px solid"
            borderColor="border.default">
            <Heading size="md" mb={4} color="text.primary">
              Garantia LinkAuto
            </Heading>
            <VStack align="start" gap={3} fontSize="xs" color="text.secondary">
              <HStack align="start" gap={2}>
                <ShieldCheck size={16} style={{ flexShrink: 0, marginTop: 2 }} />
                <Text>Instrutor com credencial ativa e verificada no DETRAN.</Text>
              </HStack>
              <HStack align="start" gap={2}>
                <Calendar size={16} style={{ flexShrink: 0, marginTop: 2 }} />
                <Text>Cancelamento gratuito com até 24 horas de antecedência.</Text>
              </HStack>
              <HStack align="start" gap={2}>
                <MessageSquare size={16} style={{ flexShrink: 0, marginTop: 2 }} />
                <Text>Chat direto vinculado à sua reserva após o agendamento.</Text>
              </HStack>
            </VStack>
          </Box>
        </SimpleGrid>

        {/* Action Callout Banner */}
        <Box
          bg="surface.panel"
          p={{ base: 6, md: 8 }}
          borderRadius="2xl"
          border="1px solid"
          borderColor="border.default"
          textAlign="center">
          <Heading size="md" mb={2} color="text.primary">
            Pronto para começar suas aulas com {instructor.full_name}?
          </Heading>
          <Text color="text.secondary" fontSize="sm" maxW="2xl" mx="auto" mb={6}>
            Escolha os melhores horários para você e faça sua solicitação de agendamento de forma rápida e segura.
          </Text>
          <Button
            bg="brand.solid"
            color="text.inverse"
            fontWeight="700"
            size="lg"
            px={8}
            onClick={handleStartBooking}
            _hover={{ bg: "brand.emphasized" }}>
            <Calendar size={18} />
            Agendar Aula com este Instrutor
          </Button>
        </Box>

        {/* Student Reviews Section */}
        <Box
          bg="surface.panel"
          p={{ base: 6, md: 8 }}
          borderRadius="2xl"
          border="1px solid"
          borderColor="border.default">
          <Heading size="md" mb={6} color="text.primary">
            Avaliações de Alunos ({instructor.reviews.length})
          </Heading>

          {instructor.reviews.length === 0 ? (
            <Box py={6} textAlign="center" color="text.secondary">
              <Text fontSize="sm">Este instrutor ainda não recebeu avaliações.</Text>
            </Box>
          ) : (
            <Stack gap={4}>
              {instructor.reviews.map((rev) => (
                <Box
                  key={rev.id}
                  p={4}
                  borderRadius="xl"
                  bg="surface.muted"
                  border="1px solid"
                  borderColor="border.default">
                  <HStack justify="space-between" align="center" mb={2}>
                    <HStack gap={3}>
                      <Box
                        w="36px"
                        h="36px"
                        borderRadius="full"
                        bg="laBlue.100"
                        color="laBlue.700"
                        display="grid"
                        placeItems="center"
                        fontSize="xs"
                        fontWeight="bold">
                        {rev.reviewer.avatar_url ? (
                          <img
                            src={rev.reviewer.avatar_url}
                            alt={rev.reviewer.full_name}
                            style={{ width: "100%", height: "100%", borderRadius: "50%", objectFit: "cover" }}
                          />
                        ) : (
                          initialsFromName(rev.reviewer.full_name)
                        )}
                      </Box>
                      <RouterLink
                        to={`/students/${rev.reviewer.slug || rev.reviewer.id}`}
                        style={{ textDecoration: "none" }}>
                        <Text
                          fontWeight="700"
                          fontSize="sm"
                          color="text.primary"
                          _hover={{ color: "brand.solid", textDecoration: "underline" }}>
                          {rev.reviewer.full_name}
                        </Text>
                      </RouterLink>
                    </HStack>

                    <HStack gap={1} color="yellow.500">
                      {Array.from({ length: 5 }, (_, i) => (
                        <Star
                          key={i}
                          size={14}
                          fill={i < rev.rating ? "currentColor" : "none"}
                        />
                      ))}
                    </HStack>
                  </HStack>

                  {rev.comment && (
                    <Text fontSize="sm" color="text.secondary" pl={12}>
                      "{rev.comment}"
                    </Text>
                  )}
                </Box>
              ))}
            </Stack>
          )}
        </Box>
      </Stack>
    </Container>
  );
}
