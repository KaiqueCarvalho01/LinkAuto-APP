import { useEffect, useState } from "react";
import { useNavigate, useParams, Link as RouterLink } from "react-router-dom";
import {
  ArrowLeft,
  Award,
  BookOpen,
  MapPin,
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
import type { ApiPublicStudentProfile } from "../types/api.types";

const initialsFromName = (name: string): string => {
  const parts = name
    .trim()
    .split(" ")
    .filter((part) => part.length > 0)
    .slice(0, 2);
  return parts.map((part) => part[0]?.toUpperCase() ?? "").join("");
};

const formatLicenseLabel = (type?: string | null): string => {
  if (!type || type === "NENHUMA" || type === "EM_PROCESSO") {
    return "Primeira Habilitação (CNH)";
  }
  return `Habilitado - Categoria ${type}`;
};

export default function StudentPublicProfilePage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [student, setStudent] = useState<ApiPublicStudentProfile | null>(null);

  useEffect(() => {
    if (!id) {
      setError("Aluno não especificado.");
      setLoading(false);
      return;
    }

    let isMounted = true;
    setLoading(true);
    setError(null);

    profileService.fetchPublicStudentProfile(id)
      .then((prof) => {
        if (isMounted) {
          setStudent(prof);
        }
      })
      .catch((err) => {
        console.error("Error loading public student profile:", err);
        if (isMounted) {
          setError("Aluno não encontrado ou perfil indisponível.");
        }
      })
      .finally(() => {
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [id]);

  if (loading) {
    return (
      <Container maxW="4xl" py={8}>
        <Stack gap={6}>
          <Skeleton h="40px" w="150px" borderRadius="md" />
          <Skeleton h="200px" borderRadius="2xl" />
          <Skeleton h="100px" borderRadius="2xl" />
          <Skeleton h="200px" borderRadius="2xl" />
        </Stack>
      </Container>
    );
  }

  if (error || !student) {
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
            {error || "Não foi possível encontrar as informações deste aluno."}
          </Text>
          <Button
            mt={4}
            variant="outline"
            onClick={() => navigate(-1)}>
            <ArrowLeft size={16} />
            Voltar
          </Button>
        </VStack>
      </Container>
    );
  }

  return (
    <Container maxW="4xl" py={8}>
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

        {/* Profile Header */}
        <Box
          bg="surface.panel"
          p={{ base: 6, md: 8 }}
          borderRadius="2xl"
          border="1px solid"
          borderColor="border.default"
          boxShadow="sm">
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
              {student.avatar_url ? (
                <img
                  src={student.avatar_url}
                  alt={student.full_name}
                  style={{ width: "100%", height: "100%", objectFit: "cover" }}
                />
              ) : (
                initialsFromName(student.full_name)
              )}
            </Box>

            <Stack gap={1.5}>
              <HStack gap={2} flexWrap="wrap" align="center">
                <Heading size={{ base: "lg", md: "xl" }} color="text.primary">
                  {student.full_name}
                </Heading>
                <Badge
                  px={2.5}
                  py={1}
                  borderRadius="full"
                  bg="laBlue.100"
                  color="laBlue.700"
                  fontWeight="700"
                  fontSize="xs">
                  {formatLicenseLabel(student.license_type)}
                </Badge>
              </HStack>

              <HStack gap={3} flexWrap="wrap" color="text.secondary" fontSize="sm">
                {student.city && (
                  <HStack gap={1}>
                    <MapPin size={15} />
                    <Text fontWeight="500">
                      {student.city}{student.state ? `, ${student.state}` : ""}
                    </Text>
                  </HStack>
                )}
                <RatingStars
                  rating={student.rating_avg}
                  reviewsCount={student.rating_count}
                />
              </HStack>
            </Stack>
          </HStack>
        </Box>

        {/* Metrics Summary Row */}
        <SimpleGrid columns={{ base: 1, sm: 3 }} gap={4}>
          <Box
            bg="surface.panel"
            p={5}
            borderRadius="2xl"
            border="1px solid"
            borderColor="border.default"
            textAlign="center">
            <HStack justify="center" color="brand.solid" mb={1}>
              <BookOpen size={20} />
            </HStack>
            <Text fontSize="xs" color="text.muted" textTransform="uppercase" fontWeight="700">
              Aulas Concluídas
            </Text>
            <Text fontSize="2xl" fontWeight="900" color="text.primary">
              {student.completed_lessons_count}
            </Text>
          </Box>

          <Box
            bg="surface.panel"
            p={5}
            borderRadius="2xl"
            border="1px solid"
            borderColor="border.default"
            textAlign="center">
            <HStack justify="center" color="yellow.500" mb={1}>
              <Star size={20} fill="currentColor" />
            </HStack>
            <Text fontSize="xs" color="text.muted" textTransform="uppercase" fontWeight="700">
              Nota Média
            </Text>
            <Text fontSize="2xl" fontWeight="900" color="text.primary">
              {student.rating_avg.toFixed(1)}
            </Text>
          </Box>

          <Box
            bg="surface.panel"
            p={5}
            borderRadius="2xl"
            border="1px solid"
            borderColor="border.default"
            textAlign="center">
            <HStack justify="center" color="laGreen.700" mb={1}>
              <Award size={20} />
            </HStack>
            <Text fontSize="xs" color="text.muted" textTransform="uppercase" fontWeight="700">
              Avaliações Recebidas
            </Text>
            <Text fontSize="2xl" fontWeight="900" color="text.primary">
              {student.rating_count}
            </Text>
          </Box>
        </SimpleGrid>

        {/* Reviews Section */}
        <Box
          bg="surface.panel"
          p={{ base: 6, md: 8 }}
          borderRadius="2xl"
          border="1px solid"
          borderColor="border.default">
          <Heading size="md" mb={6} color="text.primary">
            Feedback de Instrutores ({student.reviews.length})
          </Heading>

          {student.reviews.length === 0 ? (
            <Box py={6} textAlign="center" color="text.secondary">
              <Text fontSize="sm">Este aluno ainda não recebeu avaliações de instrutores.</Text>
            </Box>
          ) : (
            <Stack gap={4}>
              {student.reviews.map((rev) => (
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
                        to={`/instructors/${rev.reviewer.slug || rev.reviewer.id}`}
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
