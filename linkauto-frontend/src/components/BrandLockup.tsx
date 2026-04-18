import { Box, HStack, Text, VStack } from "@chakra-ui/react";

interface BrandLockupProps {
	readonly showTagline?: boolean;
	readonly compact?: boolean;
	readonly colorMode?: "light" | "dark";
}

export function BrandLockup({
	showTagline = false,
	compact = false,
	colorMode = "light",
}: BrandLockupProps) {
	const subtitleColor = colorMode === "dark" ? "whiteAlpha.700" : "ink.500";

	return (
		<HStack align="center" gap={compact ? 3 : 4}>
			<Box
				position="relative"
				w={compact ? "42px" : "54px"}
				h={compact ? "42px" : "54px"}
				borderRadius={compact ? "xl" : "2xl"}
				bgGradient="linear(135deg, brand.500 0%, brand.600 52%, accent.500 100%)"
				boxShadow="0 14px 30px rgba(23, 63, 88, 0.3)">
				<Box
					position="absolute"
					inset="8px"
					borderRadius={compact ? "lg" : "xl"}
					border="1.5px solid"
					borderColor="whiteAlpha.500"
					display="grid"
					placeItems="center">
					<Text
						fontFamily="heading"
						fontWeight="800"
						fontSize={compact ? "md" : "lg"}
						color="white">
						LA
					</Text>
				</Box>
			</Box>

			<VStack align="start" gap={0}>
				<Text
					fontFamily="heading"
					fontWeight="800"
					fontSize={compact ? "xl" : "2xl"}
					lineHeight="1"
					bgGradient="linear(95deg, brand.600, accent.500)"
					bgClip="text">
					LinkAuto
				</Text>
				{showTagline ? (
					<Text
						fontSize={compact ? "2xs" : "xs"}
						lineHeight="1.3"
						fontWeight="600"
						letterSpacing="0.08em"
						color={subtitleColor}
						textTransform="uppercase">
						Plataforma de Agendamento de Instrutores
					</Text>
				) : (
					<Text fontSize="xs" fontWeight="600" color={subtitleColor}>
						Mobilidade, confiança e escala.
					</Text>
				)}
			</VStack>
		</HStack>
	);
}
