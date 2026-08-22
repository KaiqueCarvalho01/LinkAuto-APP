import { Calendar, CircleSlash2, Plus, UserCircle2, AlertTriangle } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import {
  Box,
  Button,
  Container,
  Heading,
  HStack,
  SimpleGrid,
  Stack,
  Text,
  Skeleton,
} from "@chakra-ui/react";

import { BookingStatusBadge } from "../components/BookingStatusBadge";
import { BookingStatusTimeline } from "../components/BookingStatusTimeline";
import { bookingService } from "../services/bookingService";
import type { BookingPreview } from "../types/booking";

interface MyLessonsProps {
  readonly token: string | undefined;
  readonly onNewBooking: () => void;
}

export default function MyLessons({ token, onNewBooking }: MyLessonsProps) {
  const [bookings, setBookings] = useState<BookingPreview[]>([]);
  const [loading, setLoading] = useState(false);
  const [cancellingId, setCancellingId] = useState<string | null>(null);
  const [confirmCancelId, setConfirmCancelId] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const loadBookings = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    setErrorMessage(null);
    try {
      const data = await bookingService.getMyBookings(token);
      setBookings(data);
    } catch (err) {
      console.error("Error loading bookings:", err);
      setErrorMessage("Não foi possível carregar seus agendamentos.");
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    let isMounted = true;
    if (!token) return;
    setLoading(true);
    setErrorMessage(null);
    bookingService.getMyBookings(token)
      .then((data) => {
        if (isMounted) setBookings(data);
      })
      .catch((err) => {
        console.error("Error loading bookings:", err);
        if (isMounted) setErrorMessage("Não foi possível carregar seus agendamentos.");
      })
      .finally(() => {
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [token]);

  const handleCancel = async (bookingId: string) => {
    if (!token) return;

    setCancellingId(bookingId);
    setErrorMessage(null);
    try {
      await bookingService.cancelBooking(bookingId, token, "Cancelado pelo Aluno");
      setConfirmCancelId(null);
      // Reload list
      await loadBookings();
    } catch (err: unknown) {
      console.error("Error cancelling booking:", err);
      const msg = err instanceof Error ? err.message : "Erro ao cancelar aula. Tente novamente.";
      setErrorMessage(msg);
    } finally {
      setCancellingId(null);
    }
  };

  return (
    <Stack minH="100vh" pb={12}>
      <Container maxW="6xl" pt={8}>
        <Stack gap={6}>
          <HStack
            justify="space-between"
            align={{ base: "start", md: "center" }}>
            <Stack gap={1.5}>
              <Heading
                fontSize={{ base: "2xl", md: "3xl" }}
                color="text.primary">
                Meus agendamentos
              </Heading>
              <Text color="text.muted">
                Acompanhe a evolução das reservas e o status de
                cada aula.
              </Text>
            </Stack>

            <Button
              onClick={onNewBooking}
              bg="brand.solid"
              color="text.inverse"
              _hover={{ bg: "brand.emphasized" }}>
              <Plus size={16} />
              Nova reserva
            </Button>
          </HStack>

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

          {loading ? (
            <SimpleGrid columns={{ base: 1, lg: 2 }} gap={4}>
              {["skeleton-1", "skeleton-2"].map((key) => (
                <Skeleton key={key} h="220px" borderRadius="2xl" />
              ))}
            </SimpleGrid>
          ) : (
            <SimpleGrid columns={{ base: 1, lg: 2 }} gap={4}>
              {bookings.map((booking) => (
                <Box
                  key={booking.id}
                  bg="surface.panel"
                  border="1px solid"
                  borderColor="border.default"
                  borderRadius="2xl"
                  p={5}
                  boxShadow="sm">
                  <Stack gap={4}>
                    <HStack
                      justify="space-between"
                      align="start">
                      <Stack gap={1}>
                        <Text
                          fontWeight="700"
                          color="text.primary">
                          {booking.instructor.fullName}
                        </Text>
                        <Text
                          color="text.muted"
                          fontSize="sm"
                          fontWeight="500">
                          {booking.instructor.neighborhood}, {booking.instructor.city}
                        </Text>
                      </Stack>
                      <BookingStatusBadge status={booking.status} />
                    </HStack>

                    <HStack
                      bg="surface.muted"
                      border="1px solid"
                      borderColor="border.subtle"
                      borderRadius="xl"
                      px={3}
                      py={2.5}
                      gap={4}>
                      <HStack
                        gap={1.5}
                        color="text.secondary">
                        <Calendar
                          size={14}
                          aria-hidden="true"
                        />
                        <Text
                          fontSize="sm"
                          fontWeight="600">
                          {booking.dateLabel}
                        </Text>
                      </HStack>
                      <HStack
                        gap={1.5}
                        color="text.secondary">
                        <UserCircle2
                          size={14}
                          aria-hidden="true"
                        />
                        <Text
                          fontSize="sm"
                          fontWeight="600">
                          {booking.timeLabel}
                        </Text>
                      </HStack>
                    </HStack>

                    <BookingStatusTimeline status={booking.status} />

                    {(booking.status === "PENDENTE" || booking.status === "CONFIRMADA") && (
                      <HStack justify="flex-end" pt={2} borderTop="1px solid" borderColor="border.subtle">
                        {confirmCancelId === booking.id ? (
                          <HStack gap={2}>
                            <Text fontSize="xs" color="text.muted" mr="auto">
                              Tem certeza?
                            </Text>
                            <Button
                              size="sm"
                              colorPalette="red"
                              variant="solid"
                              loading={cancellingId === booking.id}
                              onClick={() => handleCancel(booking.id)}>
                              Sim, cancelar
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              disabled={cancellingId !== null}
                              onClick={() => setConfirmCancelId(null)}>
                              Não
                            </Button>
                          </HStack>
                        ) : (
                          <Button
                            size="sm"
                            colorPalette="red"
                            variant="ghost"
                            loading={cancellingId === booking.id}
                            disabled={cancellingId !== null}
                            onClick={() => setConfirmCancelId(booking.id)}>
                            Cancelar Aula
                          </Button>
                        )}
                      </HStack>
                    )}
                  </Stack>
                </Box>
              ))}
            </SimpleGrid>
          )}

          {!loading && bookings.length === 0 ? (
            <Box
              py={16}
              px={6}
              textAlign="center"
              bg="surface.panel"
              border="1px dashed"
              borderColor="border.default"
              borderRadius="2xl">
              <HStack justify="center" mb={2}>
                <CircleSlash2
                  size={18}
                  color="currentColor"
                  aria-hidden="true"
                />
              </HStack>
              <Text fontWeight="700" color="text.secondary">
                Nenhum agendamento encontrado.
              </Text>
            </Box>
          ) : null}
        </Stack>
      </Container>
    </Stack>
  );
}
