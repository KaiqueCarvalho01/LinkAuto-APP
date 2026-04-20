import { Star } from "lucide-react";
import { HStack, Text } from "@chakra-ui/react";

interface RatingStarsProps {
	readonly rating: number;
	readonly reviewsCount: number;
	readonly size?: "sm" | "md";
}

const sizeByToken: Record<NonNullable<RatingStarsProps["size"]>, number> = {
	sm: 16,
	md: 20,
};

export function RatingStars({
	rating,
	reviewsCount,
	size = "sm",
}: RatingStarsProps) {
	const iconSize = sizeByToken[size];
	const roundedRating = Math.round(rating);
	const emptyStarColor = "var(--chakra-colors-border-default)";

	return (
		<HStack gap={2} align="center">
			<HStack gap={1} aria-label={`Avaliacao ${rating.toFixed(1)}`}>
				{[1, 2, 3, 4, 5].map((step) => {
					const filled = step <= roundedRating;
					return (
						<Star
							key={`star-${step}`}
							size={iconSize}
							fill={filled ? "#F59E0B" : "none"}
							color={filled ? "#F59E0B" : emptyStarColor}
							aria-hidden="true"
						/>
					);
				})}
			</HStack>
			<Text
				fontSize={size === "sm" ? "sm" : "md"}
				color="text.muted"
				fontWeight="600">
				{rating.toFixed(1)} ({reviewsCount} avaliacoes)
			</Text>
		</HStack>
	);
}
