import { Box, Heading, Text } from "@chakra-ui/react";

export default function About() {
	return (
		<Box p={8} maxW="1200px" mx="auto" pt="100px">
			<Heading as="h1" size="2xl" mb={4} color="text.primary">
				About
			</Heading>
			<Text color="text.secondary">Page under construction.</Text>
		</Box>
	);
}
