import {
	HStack,
	Image,
	Text,
	VStack,
	Link as ChakraLink,
} from "@chakra-ui/react";

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
	const subtitleColor = colorMode === "dark" ? "text.primary" : "text.muted";
	const iconSize = compact ? "40px" : "52px";

	return (
		<ChakraLink
			href="/"
			_hover={{ textDecoration: "none", opacity: 0.85 }} // Remove sublinhado e adiciona feedback visual
			transition="opacity 0.2s" // Suaviza a transição do hover
		>
			<HStack align="center" gap={compact ? 3 : 4}>
				<Image
					src="/brand/LinkAuto-logo-square.webp"
					alt="LinkAuto"
					w={iconSize}
					h={iconSize}
					borderRadius={compact ? "xl" : "2xl"}
					objectFit="cover"
					boxShadow="0 10px 24px rgba(17, 24, 39, 0.18)"
				/>

				<VStack align="start" gap={0}>
					<HStack gap={0.5} lineHeight="1" align="center">
						<Text
							fontFamily="heading"
							fontWeight="800"
							fontSize={compact ? "xl" : "2xl"}
							color="laBlue.500">
							Link
						</Text>
						<Text
							fontFamily="heading"
							fontWeight="800"
							fontSize={compact ? "xl" : "2xl"}
							color="laGreen.500">
							Auto
						</Text>
					</HStack>
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
						<Text
							fontSize="xs"
							fontWeight="600"
							color={subtitleColor}>
							Mobilidade, confianca e escala.
						</Text>
					)}
				</VStack>
			</HStack>
		</ChakraLink>
	);
}
