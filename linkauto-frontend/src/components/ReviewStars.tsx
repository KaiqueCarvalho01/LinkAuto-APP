import { Star } from "lucide-react";
import { HStack } from "@chakra-ui/react";

interface ReviewStarsProps {
	readonly rating: number;
	readonly size?: number;
}

// The stars of a single review, read out as "N de 5 estrelas"
export function ReviewStars({ rating, size = 14 }: ReviewStarsProps) {
	return (
		<HStack gap={1} color="yellow.500" role="img" aria-label={`${rating} de 5 estrelas`}>
			{Array.from({ length: 5 }, (_, i) => (
				<Star
					key={i}
					size={size}
					fill={i < rating ? "currentColor" : "none"}
					aria-hidden="true"
				/>
			))}
		</HStack>
	);
}
