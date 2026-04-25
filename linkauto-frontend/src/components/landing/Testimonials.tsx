import {
	Box,
	Container,
	Flex,
	Heading,
	SimpleGrid,
	Stack,
	Text,
	Tabs,
} from "@chakra-ui/react";
import { RatingStars } from "../RatingStars";
import {
	studentTestimonials,
	instructorTestimonials,
} from "../../services/mockTestimonials";

export function Testimonials() {
	return (
		<Box py={24} bg="bg.muted">
			<Container maxW="container.xl">
				<Tabs.Root defaultValue="students" variant="enclosed">
					<Stack gap={12} align="center">
						<Stack textAlign="center" gap={4}>
							<Heading fontSize="3xl" fontWeight="800">
								Depoimentos
							</Heading>
							<Text color="text.muted" fontSize="lg">
								Confira o que nossa comunidade está falando.
							</Text>
						</Stack>

						<Tabs.List
							bg="bg.canvas"
							p={1}
							rounded="full"
							border="1px solid"
							borderColor="border.subtle">
							<Tabs.Trigger
								value="students"
								px={8}
								rounded="full"
								_selected={{
									bg: "brand.500",
									color: "white",
									borderColor: "brand.500",
								}}
								fontWeight="bold"
								cursor="pointer">
								Alunos
							</Tabs.Trigger>
							<Tabs.Trigger
								value="instructors"
								px={8}
								rounded="full"
								_selected={{
									bg: "brand.500",
									color: "white",
									borderColor: "brand.500",
								}}
								fontWeight="bold"
								cursor="pointer">
								Instrutores
							</Tabs.Trigger>
						</Tabs.List>

						<Tabs.Content value="students" w="full">
							<Stack gap={8}>
								<Heading
									fontSize="xl"
									fontWeight="bold"
									textAlign="center"
									color="brand.600">
									O que nossos alunos dizem
								</Heading>
								<SimpleGrid columns={{ base: 1, md: 3 }} gap={8}>
									{studentTestimonials.map((t) => (
										<TestimonialCard
											key={t.id}
											testimonial={t}
										/>
									))}
								</SimpleGrid>
							</Stack>
						</Tabs.Content>

						<Tabs.Content value="instructors" w="full">
							<Stack gap={8}>
								<Heading
									fontSize="xl"
									fontWeight="bold"
									textAlign="center"
									color="laBlue.600">
									A voz de quem ensina
								</Heading>
								<SimpleGrid columns={{ base: 1, md: 3 }} gap={8}>
									{instructorTestimonials.map((t) => (
										<TestimonialCard
											key={t.id}
											testimonial={t}
										/>
									))}
								</SimpleGrid>
							</Stack>
						</Tabs.Content>
					</Stack>
				</Tabs.Root>
			</Container>
		</Box>
	);
}

function TestimonialCard({ testimonial }: { testimonial: any }) {
	return (
		<Box
			bg="surface.panel"
			p={8}
			borderRadius="2xl"
			border="1px solid"
			borderColor="border.subtle"
			shadow="sm"
			transition="all 0.3s"
			_hover={{
				transform: "translateY(-4px)",
				boxShadow: "md",
				borderColor: "brand.200",
			}}>
			<Stack gap={6}>
				<RatingStars rating={testimonial.rating} reviewsCount={0} />
				<Text fontStyle="italic" color="text.primary" lineHeight="tall">
					"{testimonial.text}"
				</Text>
				<Flex gap={4} align="center">
					<Flex
						w={12}
						h={12}
						bg="laBlue.500"
						color="white"
						borderRadius="full"
						align="center"
						justify="center"
						fontWeight="bold"
						fontSize="lg"
						border="2px solid"
						borderColor="surface.panel"
						shadow="sm">
						{testimonial.name.charAt(0)}
					</Flex>
					<Box>
						<Text fontWeight="bold" fontSize="sm">
							{testimonial.name}
						</Text>
						<Text fontSize="xs" color="text.muted">
							{testimonial.role}
						</Text>
					</Box>
				</Flex>
			</Stack>
		</Box>
	);
}
