import { Badge, Box, Button, HStack, Stack, Text } from "@chakra-ui/react";
import { CheckCircle2, MapPin } from "lucide-react";

import { RatingStars } from "./RatingStars";
import type { InstructorSummary } from "../types/instructor";

interface InstructorCardProps {
	readonly instructor: InstructorSummary;
	readonly selected?: boolean;
	readonly onOpenProfile: (instructor: InstructorSummary) => void;
	readonly onBook: (instructor: InstructorSummary) => void;
}

const initialsFromName = (name: string): string => {
	const parts = name
		.trim()
		.split(" ")
		.filter((part) => part.length > 0)
		.slice(0, 2);
	return parts.map((part) => part[0]?.toUpperCase() ?? "").join("");
};

export function InstructorCard({
	instructor,
	selected = false,
	onOpenProfile,
	onBook,
}: InstructorCardProps) {
	return (
		<Box
			border="1px solid"
			borderColor={selected ? "brand.solid" : "border.default"}
			bg="surface.panel"
			borderRadius="2xl"
			p={4}
			boxShadow={selected ? "0 14px 30px rgba(26, 109, 181, 0.16)" : "sm"}
			transition="all 0.2s ease"
			_hover={{
				boxShadow: "md",
				borderColor: "brand.solid",
			}}>
			<Stack gap={3.5}>
				<HStack justify="space-between" align="start">
					<HStack align="start" gap={3}>
						<Box
							w="56px"
							h="56px"
							borderRadius="full"
							display="grid"
							placeItems="center"
							bg="laBlue.100"
							color="laBlue.700"
							fontWeight="800"
							border="2px solid"
							borderColor="laGreen.100">
							{initialsFromName(instructor.fullName)}
						</Box>

						<Stack gap={1}>
							<Text
								fontSize="lg"
								fontWeight="700"
								color="text.primary">
								{instructor.fullName}
							</Text>
							<RatingStars
								rating={instructor.rating}
								reviewsCount={instructor.reviewsCount}
							/>
							<HStack gap={1.5} color="text.muted">
								<MapPin size={14} aria-hidden="true" />
								<Text fontSize="sm" fontWeight="500">
									{instructor.distanceKm.toFixed(1)} km · R$
									{instructor.hourlyRate}/h
								</Text>
							</HStack>
						</Stack>
					</HStack>

					{instructor.detranApproved ? (
						<Badge
							px={2}
							py={1}
							borderRadius="full"
							bg="laGreen.100"
							color="laGreen.700"
							fontWeight="700"
							fontSize="xs"
							display="inline-flex"
							alignItems="center"
							gap={1}>
							<CheckCircle2 size={12} aria-hidden="true" />
							DETRAN
						</Badge>
					) : null}
				</HStack>

				<HStack gap={2} flexWrap="wrap">
					{instructor.specialties.map((specialty) => (
						<Badge
							key={specialty}
							px={2.5}
							py={1}
							bg="laBlue.100"
							color="laBlue.700"
							borderRadius="full"
							fontWeight="600"
							fontSize="xs">
							{specialty}
						</Badge>
					))}
				</HStack>

				<HStack gap={2}>
					<Button
						flex="1"
						h="40px"
						variant="outline"
						borderColor="border.default"
						color="text.secondary"
						onClick={() => onOpenProfile(instructor)}>
						Ver perfil
					</Button>
					<Button
						flex="1"
						h="40px"
						bg="brand.solid"
						color="text.inverse"
						fontWeight="700"
						onClick={() => onBook(instructor)}
						_hover={{ bg: "brand.emphasized" }}>
						Agendar
					</Button>
				</HStack>
			</Stack>
		</Box>
	);
}
