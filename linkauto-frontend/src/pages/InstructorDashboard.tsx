import { useState, type ReactNode } from "react";
import { AlertTriangle, Calendar, Check, Clock, Star, X } from "lucide-react";
import { Box, Button, HStack, Stack, Text, Textarea, Badge } from "@chakra-ui/react";

import type { AdminStats, DashboardRequest, InstructorStats } from "../types/session";

interface InstructorData {
	readonly name: string;
	readonly rating: number;
}

interface InstructorDashboardProps {
	readonly instructorData?: InstructorData;
	readonly requests?: DashboardRequest[];
	readonly onAccept?: (requestId: string) => Promise<void> | void;
	readonly onReject?: (requestId: string, reason?: string) => Promise<void> | void;
	readonly dashboardTitle?: string;
	readonly pendingLabel?: string;
	readonly isAdminDashboard?: boolean;
	readonly pendingInstructors?: number;
	readonly approvedInstructors?: number;
	readonly adminStats?: AdminStats | undefined;
	readonly instructorStats?: InstructorStats | undefined;
	// Extra sections shown below the requests (upcoming lessons and the agenda)
	readonly agenda?: ReactNode;
	// Ask for a reason before rejecting (sent to the instructor by e-mail)
	readonly requireRejectReason?: boolean;
	// Total pending, when the list shows only a page of them
	readonly pendingTotal?: number;
	// Error from the last approve/reject, shown above the list
	readonly actionError?: string | null;
}

export default function InstructorDashboard({
	instructorData,
	requests = [],
	onAccept,
	onReject,
	dashboardTitle = "Painel do Instrutor",
	pendingLabel = "Solicitacoes",
	isAdminDashboard = false,
	pendingInstructors = 0,
	approvedInstructors = 0,
	adminStats,
	instructorStats,
	agenda,
	requireRejectReason = false,
	pendingTotal,
	actionError = null,
}: InstructorDashboardProps) {
	const [processingId, setProcessingId] = useState<string | null>(null);
	const [rejectingId, setRejectingId] = useState<string | null>(null);
	const [rejectReason, setRejectReason] = useState("");

	const titleName = instructorData?.name ?? "LinkAuto";
	const rating = instructorData?.rating ?? 5;

	const handleAction = async (
		action: ((requestId: string, reason?: string) => Promise<void> | void) | undefined,
		requestId: string,
		reason?: string,
	) => {
		if (!action) {
			return;
		}

		setProcessingId(requestId);
		try {
			await action(requestId, reason);
		} finally {
			setProcessingId(null);
		}
	};

	const MIN_REJECT_REASON = 3;

	return (
		<Stack
			minH="100vh"
			px={{ base: 4, md: 8 }}
			py={{ base: 6, md: 8 }}
			gap={6}>
			<Box
				position="relative"
				overflow="hidden"
				borderRadius="3xl"
				bgGradient="linear(145deg, #102c40 0%, #1a567f 54%, #338640 100%)"
				p={{ base: 6, md: 8 }}
				boxShadow="0 24px 56px rgba(19, 62, 93, 0.3)">
				<Box
					position="absolute"
					w="180px"
					h="180px"
					right="-52px"
					top="-58px"
					borderRadius="full"
					bg="whiteAlpha.250"
				/>
				<Stack position="relative" zIndex={1} gap={5}>
					<HStack justify="space-between" align="start">
						<Stack gap={1}>
							<Text
								color="text.muted"
								fontSize="xs"
								fontWeight="800"
								letterSpacing="0.14em"
								textTransform="uppercase">
								{dashboardTitle}
							</Text>
							<Text
								color="text.secondary"
								fontFamily="heading"
								fontSize={{ base: "2xl", md: "3xl" }}
								fontWeight="600">
								{titleName}
							</Text>
						</Stack>
						<HStack
							px={3}
							py={2}
							bg="whiteAlpha.200"
							borderRadius="xl"
							border="1px solid"
							borderColor="border.default-subtle"
							color="text.muted">
							<Star size={16} fill="currentColor" />
							<Text fontWeight="800" fontSize="sm">
								{rating.toFixed(1)}
							</Text>
						</HStack>
					</HStack>

					<HStack
						gap={3}
						align="stretch"
						flexWrap={{ base: "wrap", md: "nowrap" }}>
						{isAdminDashboard ? (
							<>
								<Box
									flex="1"
									minW={{ base: "100%", md: "0" }}
									bg="whiteAlpha.200"
									borderRadius="2xl"
									p={4}
									border="1px solid"
									borderColor="border.default">
									<Text
										color="text.secondary"
										fontSize="xs"
										textTransform="uppercase"
										fontWeight="700">
										Instrutores Aprovados
									</Text>
									<Text
										color="text.primary"
										fontWeight="900"
										fontSize="2xl"
										lineHeight="1">
										{adminStats?.approvedInstructors ?? approvedInstructors}
									</Text>
								</Box>
								<Box
									flex="1"
									minW={{ base: "100%", md: "0" }}
									bg="whiteAlpha.200"
									borderRadius="2xl"
									p={4}
									border="1px solid"
									borderColor="border.default">
									<Text
										color="text.secondary"
										fontSize="xs"
										textTransform="uppercase"
										fontWeight="700">
										Instrutores Pendentes
									</Text>
									<Text
										color="text.primary"
										fontWeight="900"
										fontSize="2xl"
										lineHeight="1">
										{adminStats?.pendingInstructors ?? pendingInstructors}
									</Text>
								</Box>
								<Box
									flex="1"
									minW={{ base: "100%", md: "0" }}
									bg="whiteAlpha.200"
									borderRadius="2xl"
									p={4}
									border="1px solid"
									borderColor="border.default">
									<Text
										color="text.secondary"
										fontSize="xs"
										textTransform="uppercase"
										fontWeight="700">
										Alunos Cadastrados
									</Text>
									<Text
										color="text.primary"
										fontWeight="900"
										fontSize="2xl"
										lineHeight="1">
										{adminStats?.totalStudents ?? 0}
									</Text>
								</Box>
								<Box
									flex="1"
									minW={{ base: "100%", md: "0" }}
									bg="whiteAlpha.200"
									borderRadius="2xl"
									p={4}
									border="1px solid"
									borderColor="border.default">
									<Text
										color="text.secondary"
										fontSize="xs"
										textTransform="uppercase"
										fontWeight="700">
										Total de Reservas
									</Text>
									<Text
										color="text.primary"
										fontWeight="900"
										fontSize="2xl"
										lineHeight="1">
										{adminStats?.totalBookings ?? 0}
									</Text>
								</Box>
							</>
						) : (
							<>
								<Box
									flex="1"
									minW={{ base: "100%", md: "0" }}
									bg="whiteAlpha.200"
									borderRadius="2xl"
									p={4}
									border="1px solid"
									borderColor="border.default">
									<Text
										color="text.secondary"
										fontSize="xs"
										textTransform="uppercase"
										fontWeight="700">
										Aulas Ministradas
									</Text>
									<Text
										color="text.primary"
										fontWeight="900"
										fontSize="2xl"
										lineHeight="1">
										{instructorStats?.totalLessons ?? 0}
									</Text>
								</Box>
								<Box
									flex="1"
									minW={{ base: "100%", md: "0" }}
									bg="whiteAlpha.200"
									borderRadius="2xl"
									p={4}
									border="1px solid"
									borderColor="border.default">
									<Text
										color="text.secondary"
										fontSize="xs"
										textTransform="uppercase"
										fontWeight="700">
										Horas Ministradas
									</Text>
									<Text
										color="text.primary"
										fontWeight="900"
										fontSize="2xl"
										lineHeight="1">
										{instructorStats?.totalHours ?? 0}h
									</Text>
								</Box>
								<Box
									flex="1"
									minW={{ base: "100%", md: "0" }}
									bg="whiteAlpha.200"
									borderRadius="2xl"
									p={4}
									border="1px solid"
									borderColor="border.default">
									<Text
										color="text.secondary"
										fontSize="xs"
										textTransform="uppercase"
										fontWeight="700">
										Alunos Únicos
									</Text>
									<Text
										color="text.primary"
										fontWeight="900"
										fontSize="2xl"
										lineHeight="1">
										{instructorStats?.uniqueStudents ?? 0}
									</Text>
								</Box>
								<Box
									flex="1"
									minW={{ base: "100%", md: "0" }}
									bg="whiteAlpha.200"
									borderRadius="2xl"
									p={4}
									border="1px solid"
									borderColor="border.default">
									<Text
										color="text.secondary"
										fontSize="xs"
										textTransform="uppercase"
										fontWeight="700">
										Reservas Pendentes
									</Text>
									<Text
										color="text.primary"
										fontWeight="900"
										fontSize="2xl"
										lineHeight="1">
										{instructorStats?.pendingBookings ?? 0}
									</Text>
								</Box>
							</>
						)}
					</HStack>
				</Stack>
			</Box>

			<Stack gap={4}>
				<HStack justify="space-between" px={1} align="center">
					<Text
						color="text.primary"
						fontWeight="800"
						fontSize="lg"
						fontFamily="heading">
						{pendingLabel}
					</Text>
					<Box
						px={3}
						py={1}
						borderRadius="full"
						bg="state.warning.bg"
						border="1px solid"
						borderColor="state.warning.border">
						<Text
							color="state.warning.fg"
							fontSize="xs"
							fontWeight="800"
							letterSpacing="0.08em">
							{pendingTotal ?? requests.length} PENDENTES
						</Text>
					</Box>
				</HStack>

				{actionError && (
					<HStack
						p={4}
						bg="red.50"
						color="red.700"
						borderRadius="xl"
						border="1px solid"
						borderColor="red.200"
						gap={2}
						role="alert">
						<AlertTriangle size={18} aria-hidden="true" />
						<Text fontSize="sm" fontWeight="600">
							{actionError}
						</Text>
					</HStack>
				)}

				{requests.length > 0 ? (
					requests.map((request) => {
						const displayName = request.studentName ?? request.name;
						const isProcessing = processingId === request.id;
						return (
							<Box
								key={request.id}
								bg="surface.panel"
								borderRadius="3xl"
								border="1px solid"
								borderColor="border.subtle"
								boxShadow="0 16px 36px rgba(47, 63, 79, 0.08)"
								p={5}>
								<Stack gap={4}>
									<HStack gap={3} align="center">
										<Box
											w="44px"
											h="44px"
											display="grid"
											placeItems="center"
											borderRadius="xl"
											bg="surface.muted"
											color="text.secondary"
											fontWeight="800">
											{displayName.charAt(0)}
										</Box>
										<Stack gap={0}>
											<Text
												fontWeight="800"
												color="text.primary">
												{displayName}
											</Text>
											<Text
												fontSize="xs"
												fontWeight="700"
												color="text.muted"
												textTransform="uppercase">
												{request.neighborhood || request.city}
											</Text>
										</Stack>
									</HStack>

									{request.specialties && request.specialties.length > 0 && (
										<HStack flexWrap="wrap" gap={1.5} py={1}>
											{request.specialties.map((spec) => (
												<Badge key={spec} colorPalette="brand" variant="subtle" rounded="md" px={2} py={0.5} fontSize="2xs">
													{spec}
												</Badge>
											))}
										</HStack>
									)}

									<HStack
										gap={4}
										px={3}
										py={2.5}
										bg="surface.muted"
										borderRadius="xl"
										border="1px solid"
										borderColor="border.subtle">
										<HStack gap={1.5}>
											<Calendar
												size={14}
												color="var(--chakra-colors-brand-solid)"
											/>
											<Text
												fontSize="sm"
												fontWeight="700"
												color="text.secondary">
												{request.date}
											</Text>
										</HStack>
										<HStack gap={1.5}>
											<Clock
												size={14}
												color="var(--chakra-colors-brand-solid)"
											/>
											<Text
												fontSize="sm"
												fontWeight="700"
												color="text.secondary">
												{request.time}
											</Text>
										</HStack>
									</HStack>

									{rejectingId === request.id ? (
										<Stack gap={2}>
											<Text asChild fontSize="xs" fontWeight="700" color="text.secondary">
												<label htmlFor={`reject-reason-${request.id}`}>
													Motivo da recusa (enviado ao instrutor)
												</label>
											</Text>
											<Textarea
												id={`reject-reason-${request.id}`}
												value={rejectReason}
												onChange={(e) => setRejectReason(e.target.value)}
												maxLength={500}
												placeholder="Ex.: a credencial DETRAN enviada está vencida."
												bg="surface.canvas"
												borderRadius="xl"
											/>
											<HStack gap={2} justify="flex-end">
												<Button
													size="sm"
													variant="outline"
													disabled={isProcessing}
													onClick={() => setRejectingId(null)}>
													Voltar
												</Button>
												<Button
													size="sm"
													colorPalette="red"
													loading={isProcessing}
													disabled={rejectReason.trim().length < MIN_REJECT_REASON}
													onClick={() => {
														void handleAction(onReject, request.id, rejectReason.trim()).then(
															() => setRejectingId(null),
														);
													}}>
													Confirmar recusa
												</Button>
											</HStack>
										</Stack>
									) : null}

									<HStack gap={3} hidden={rejectingId === request.id}>
										<Button
											flex="1"
											h="46px"
											variant="outline"
											borderColor="border.default"
											color="text.secondary"
											onClick={() => {
												if (requireRejectReason) {
													setRejectReason("");
													setRejectingId(request.id);
													return;
												}
												void handleAction(
													onReject,
													request.id,
												);
											}}
											disabled={isProcessing}>
											<X size={16} />
											Recusar
										</Button>
										<Button
											flex="1"
											h="46px"
											bgGradient="linear(95deg, brand.700, brand.500)"
											color="text.inverse"
											onClick={() => {
												void handleAction(
													onAccept,
													request.id,
												);
											}}
											loading={isProcessing}>
											<Check size={16} />
											Aprovar
										</Button>
									</HStack>
								</Stack>
							</Box>
						);
					})
				) : (
					<Box
						bg="surface.panel"
						borderRadius="3xl"
						border="1px dashed"
						borderColor="border.default"
						py={12}
						px={6}
						textAlign="center">
						<Text color="text.secondary" fontWeight="700">
							Nenhuma solicitacao pendente no momento.
						</Text>
					</Box>
				)}
			</Stack>

			{agenda}
		</Stack>
	);
}
