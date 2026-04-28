import { Calendar, CircleSlash2, Plus, UserCircle2 } from "lucide-react";
import {
	Box,
	Button,
	Container,
	Heading,
	HStack,
	SimpleGrid,
	Stack,
	Text,
} from "@chakra-ui/react";

import { BookingStatusBadge } from "../components/BookingStatusBadge";
import { BookingStatusTimeline } from "../components/BookingStatusTimeline";
import { mockBookings } from "../services/mockData";

interface MyLessonsProps {
	readonly onNewBooking: () => void;
}

export default function MyLessons({ onNewBooking }: MyLessonsProps) {
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
								Acompanhe a evolucao das reservas e o status de
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

					<SimpleGrid columns={{ base: 1, lg: 2 }} gap={4}>
						{mockBookings.map((booking) => (
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
												{
													booking.instructor
														.neighborhood
												}
												, {booking.instructor.city}
											</Text>
										</Stack>
										<BookingStatusBadge
											status={booking.status}
										/>
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

									<BookingStatusTimeline
										status={booking.status}
									/>
								</Stack>
							</Box>
						))}
					</SimpleGrid>

					{mockBookings.length === 0 ? (
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
