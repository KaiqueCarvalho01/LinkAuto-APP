import { useEffect, useState } from "react";
import { Link as RouterLink } from "react-router-dom";
import { ArrowLeft, Calendar, Clock3, TriangleAlert, AlertTriangle } from "lucide-react";
import {
  Box,
  Button,
  Container,
  Heading,
  HStack,
  Stack,
  Text,
  Skeleton,
  SimpleGrid,
} from "@chakra-ui/react";

import { BookingStatusTimeline } from "../components/BookingStatusTimeline";
import { RatingStars } from "../components/RatingStars";
import { SlotPicker } from "../components/SlotPicker";
import { bookingSelectionIsValid } from "../features/bookings/bookingRules";
import { slotService } from "../services/slotService";
import { bookingService } from "../services/bookingService";
import type { InstructorSummary } from "../types/instructor";
import type { BookingSlot } from "../types/booking";

interface LessonDetailsProps {
  readonly instructor: InstructorSummary | undefined;
  readonly token: string | undefined;
  readonly blockedUntil?: string | null;
  readonly onBack: () => void;
  readonly onBookingCreated: () => void;
}

export default function LessonDetails({
  instructor,
  token,
  blockedUntil = null,
  onBack,
  onBookingCreated,
}: LessonDetailsProps) {
  const [selectedSlotIds, setSelectedSlotIds] = useState<string[]>([]);
  const [slots, setSlots] = useState<BookingSlot[]>([]);
  const [loadingSlots, setLoadingSlots] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    
    const fetchSlots = async () => {
      if (!instructor) return;
      setLoadingSlots(true);
      setErrorMessage(null);
      try {
        const data = await slotService.getInstructorSlots(instructor.id);
        if (active) {
          setSlots(data);
        }
      } catch (err) {
        console.error("Error loading instructor slots:", err);
        if (active) {
          setErrorMessage("Não foi possível carregar a agenda do instrutor.");
        }
      } finally {
        if (active) {
          setLoadingSlots(false);
        }
      }
    };

    void fetchSlots();

    return () => {
      active = false;
    };
  }, [instructor]);

  const canCreateBooking = instructor
    ? bookingSelectionIsValid(slots, selectedSlotIds)
    : false;

  const handleRequestBooking = async () => {
    if (!instructor || !token || !canCreateBooking) return;

    setIsSubmitting(true);
    setErrorMessage(null);
    try {
      await bookingService.createBooking({
        instructor_id: instructor.id,
        slot_ids: selectedSlotIds,
        location_description: `Aula prática de direção com ${instructor.fullName}`,
      }, token);
      
      onBookingCreated();
    } catch (err: unknown) {
      const error = err as { status?: number; payload?: { error?: { code?: string } }; message?: string };
      console.error("Error creating booking:", error);
      if (error.status === 403 && error.payload?.error?.code === "STUDENT_PENALIZED") {
        setErrorMessage("Sua conta está penalizada e temporariamente impedida de agendar novas aulas.");
      } else if (error.status === 422 && error.payload?.error?.code === "SLOT_VALIDATION") {
        setErrorMessage("Os horários selecionados são inválidos ou não são consecutivos.");
      } else {
        setErrorMessage(error.message || "Erro ao solicitar agendamento. Tente novamente.");
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!instructor) {
    return (
      <Container maxW="4xl" pt={8}>
        <Text color="text.muted">Nenhum instrutor selecionado.</Text>
      </Container>
    );
  }

  return (
    <Stack minH="100vh" pb={12}>
      <Container maxW="4xl" pt={8}>
        <Stack gap={6}>
          <Button
            alignSelf="flex-start"
            variant="ghost"
            onClick={onBack}
            color="text.secondary">
            <ArrowLeft size={16} />
            Voltar para busca
          </Button>

          <Box
            bg="surface.panel"
            border="1px solid"
            borderColor="border.default"
            borderRadius="2xl"
            p={{ base: 5, md: 6 }}>
            <Stack gap={3.5}>
              <Heading
                fontSize={{ base: "2xl", md: "3xl" }}
                color="text.primary">
                Solicitar agendamento
              </Heading>
              <Text color="text.muted">
                Selecione pelo menos 2 slots consecutivos para
                montar sua aula com o instrutor.
              </Text>

              <Stack
                gap={2}
                bg="brand.muted"
                border="1px solid"
                borderColor="brand.solid"
                borderRadius="xl"
                px={4}
                py={3}>
                <RouterLink
                  to={`/instructors/${instructor.slug || instructor.id}`}
                  style={{ textDecoration: "none" }}>
                  <Text
                    fontWeight="700"
                    color="brand.emphasized"
                    _hover={{ textDecoration: "underline" }}>
                    {instructor.fullName}
                  </Text>
                </RouterLink>
                <RatingStars
                  rating={instructor.rating}
                  reviewsCount={instructor.reviewsCount}
                />
                <HStack
                  color="text.secondary"
                  fontSize="sm"
                  fontWeight="600"
                  gap={4}>
                  <HStack gap={1.5}>
                    <Calendar
                      size={14}
                      aria-hidden="true"
                    />
                    <Text>Membro Credenciado</Text>
                  </HStack>
                  <HStack gap={1.5}>
                    <Clock3 size={14} aria-hidden="true" />
                    <Text>{instructor.city}</Text>
                  </HStack>
                </HStack>
              </Stack>
            </Stack>
          </Box>

          {errorMessage && (
            <HStack
              p={4}
              bg="red.50"
              color="red.700"
              borderRadius="xl"
              border="1px solid"
              borderColor="red.200"
              gap={2}>
              <AlertTriangle size={18} />
              <Text fontSize="sm" fontWeight="600">
                {errorMessage}
              </Text>
            </HStack>
          )}

          {blockedUntil && (
            <HStack
              borderRadius="xl"
              bg="state.danger.bg"
              border="1px solid"
              borderColor="state.danger.border"
              align="start"
              px={4}
              py={3}
              gap={3}>
              <TriangleAlert
                size={18}
                color="currentColor"
                aria-hidden="true"
              />
              <Text
                color="state.danger.fg"
                fontSize="sm"
                fontWeight="600">
                Sua conta está com reservas bloqueadas até{" "}
                {blockedUntil}. Cancelamentos com menos de 24h
                geram bloqueio de 7 dias.
              </Text>
            </HStack>
          )}

          <Box
            bg="surface.panel"
            border="1px solid"
            borderColor="border.default"
            borderRadius="2xl"
            p={{ base: 5, md: 6 }}>
            <Stack gap={5}>
              <Stack gap={1}>
                <Heading fontSize="xl" color="text.primary">
                  Selecione os horários
                </Heading>
                <Text color="text.muted">
                  Slots reservados ou bloqueados ficam
                  indisponíveis para seleção.
                </Text>
              </Stack>

              {loadingSlots ? (
                <SimpleGrid columns={{ base: 2, sm: 3, md: 4 }} gap={3}>
                  {["s-slot-1", "s-slot-2", "s-slot-3"].map((key) => (
                    <Skeleton key={key} h="46px" borderRadius="md" />
                  ))}
                </SimpleGrid>
              ) : (
                <SlotPicker
                  slots={slots}
                  selectedIds={selectedSlotIds}
                  onSelectedIdsChange={setSelectedSlotIds}
                />
              )}

              <HStack
                justify="space-between"
                bg="surface.muted"
                border="1px solid"
                borderColor="border.subtle"
                borderRadius="xl"
                px={4}
                py={3}>
                <HStack gap={2} color="text.muted">
                  <TriangleAlert
                    size={16}
                    aria-hidden="true"
                  />
                  <Text fontSize="sm" fontWeight="600">
                    Status inicial da reserva: Pendente
                  </Text>
                </HStack>
                <Text
                  fontSize="sm"
                  color="text.secondary"
                  fontWeight="700">
                  {selectedSlotIds.length} slot(s) selecionado(s)
                </Text>
              </HStack>

              <BookingStatusTimeline status="PENDENTE" />

              <HStack justify="flex-end" gap={3}>
                <Button
                  variant="outline"
                  borderColor="border.default"
                  color="text.secondary"
                  onClick={onBack}>
                  Cancelar
                </Button>
                <Button
                  disabled={
                    !canCreateBooking ||
                    Boolean(blockedUntil) ||
                    isSubmitting
                  }
                  loading={isSubmitting}
                  bg="brand.solid"
                  color="text.inverse"
                  _hover={{ bg: "brand.emphasized" }}
                  onClick={handleRequestBooking}>
                  Solicitar agendamento
                </Button>
              </HStack>
            </Stack>
          </Box>
        </Stack>
      </Container>
    </Stack>
  );
}
