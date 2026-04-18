import { useState } from "react";
import { Award, Calendar, Check, Clock, Star, Users, X } from "lucide-react";
import { Box, Button, HStack, Stack, Text } from "@chakra-ui/react";

import type { DashboardRequest } from "../types/session";

interface InstructorData {
	readonly name: string;
	readonly rating: number;
}

interface InstructorDashboardProps {
	readonly instructorData?: InstructorData;
	readonly requests?: DashboardRequest[];
	readonly onAccept?: (requestId: string) => Promise<void> | void;
	readonly onReject?: (requestId: string) => Promise<void> | void;
	readonly onViewStudents?: () => void;
	readonly dashboardTitle?: string;
	readonly pendingLabel?: string;
}

export default function InstructorDashboard({
	instructorData,
	requests = [],
	onAccept,
	onReject,
	onViewStudents,
	dashboardTitle = "Painel do Instrutor",
	pendingLabel = "Solicitacoes",
}: InstructorDashboardProps) {
	const [processingId, setProcessingId] = useState<string | null>(null);

	const titleName = instructorData?.name ?? "LinkAuto";
	const rating = instructorData?.rating ?? 5;

	const handleAction = async (
		action: ((requestId: string) => Promise<void> | void) | undefined,
		requestId: string,
	) => {
		if (!action) {
			return;
		}

		setProcessingId(requestId);
		try {
			await action(requestId);
		} finally {
			setProcessingId(null);
		}
	};

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
								color="whiteAlpha.700"
								fontSize="xs"
								fontWeight="800"
								letterSpacing="0.14em"
								textTransform="uppercase">
								{dashboardTitle}
							</Text>
							<Text
								color="white"
								fontFamily="heading"
								fontSize={{ base: "2xl", md: "3xl" }}
								fontWeight="800">
								{titleName}
							</Text>
						</Stack>
						<HStack
							px={3}
							py={2}
							bg="whiteAlpha.200"
							borderRadius="xl"
							border="1px solid"
							borderColor="whiteAlpha.300"
							color="white">
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
						<Box
							flex="1"
							minW={{ base: "100%", md: "0" }}
							bg="whiteAlpha.200"
							borderRadius="2xl"
							p={4}
							border="1px solid"
							borderColor="whiteAlpha.300">
							<Text
								color="whiteAlpha.700"
								fontSize="xs"
								textTransform="uppercase"
								fontWeight="700">
								Total de aulas
							</Text>
							<Text
								color="white"
								fontWeight="900"
								fontSize="2xl"
								lineHeight="1">
								42
							</Text>
						</Box>
						<Box
							flex="1"
							minW={{ base: "100%", md: "0" }}
							bg="whiteAlpha.200"
							borderRadius="2xl"
							p={4}
							border="1px solid"
							borderColor="whiteAlpha.300">
							<Text
								color="whiteAlpha.700"
								fontSize="xs"
								textTransform="uppercase"
								fontWeight="700">
								Horas ministradas
							</Text>
							<Text
								color="white"
								fontWeight="900"
								fontSize="2xl"
								lineHeight="1">
								84h
							</Text>
						</Box>
					</HStack>
				</Stack>
			</Box>

			<Stack gap={4}>
				<HStack justify="space-between" px={1} align="center">
					<Text
						color="ink.800"
						fontWeight="800"
						fontSize="lg"
						fontFamily="heading">
						{pendingLabel}
					</Text>
					<Box
						px={3}
						py={1}
						borderRadius="full"
						bg="orange.50"
						border="1px solid"
						borderColor="orange.200">
						<Text
							color="orange.600"
							fontSize="xs"
							fontWeight="800"
							letterSpacing="0.08em">
							{requests.length} PENDENTES
						</Text>
					</Box>
				</HStack>

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
								borderColor="ink.100"
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
											bg="ink.50"
											color="ink.700"
											fontWeight="800">
											{displayName.charAt(0)}
										</Box>
										<Stack gap={0}>
											<Text
												fontWeight="800"
												color="ink.900">
												{displayName}
											</Text>
											<Text
												fontSize="xs"
												fontWeight="700"
												color="ink.500"
												textTransform="uppercase">
												{request.neighborhood ??
													request.city}
											</Text>
										</Stack>
									</HStack>

									<HStack
										gap={4}
										px={3}
										py={2.5}
										bg="ink.50"
										borderRadius="xl"
										border="1px solid"
										borderColor="ink.100">
										<HStack gap={1.5}>
											<Calendar
												size={14}
												color="#2f87cc"
											/>
											<Text
												fontSize="sm"
												fontWeight="700"
												color="ink.700">
												{request.date}
											</Text>
										</HStack>
										<HStack gap={1.5}>
											<Clock size={14} color="#2f87cc" />
											<Text
												fontSize="sm"
												fontWeight="700"
												color="ink.700">
												{request.time}
											</Text>
										</HStack>
									</HStack>

									<HStack gap={3}>
										<Button
											flex="1"
											h="46px"
											variant="outline"
											borderColor="ink.200"
											color="ink.600"
											onClick={() => {
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
											color="white"
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
						borderColor="ink.200"
						py={12}
						px={6}
						textAlign="center">
						<Text color="ink.600" fontWeight="700">
							Nenhuma solicitacao pendente no momento.
						</Text>
					</Box>
				)}
			</Stack>

			<HStack
				gap={3}
				align="stretch"
				flexWrap={{ base: "wrap", md: "nowrap" }}>
				<Button
					flex="1"
					h={{ base: "52px", md: "58px" }}
					variant="outline"
					borderColor="ink.200"
					bg="surface.panel"
					onClick={onViewStudents}>
					<Users size={18} />
					Meus alunos
				</Button>
				<Button
					flex="1"
					h={{ base: "52px", md: "58px" }}
					variant="outline"
					borderColor="ink.200"
					bg="surface.panel"
					disabled>
					<Award size={18} />
					Conquistas
				</Button>
			</HStack>
		</Stack>
	);
}
