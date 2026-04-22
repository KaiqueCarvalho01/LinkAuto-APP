import { ArrowRight, Compass, ShieldCheck, TimerReset } from "lucide-react";
import {
	Box,
	Button,
	Container,
	Grid,
	Heading,
	HStack,
	Image,
	SimpleGrid,
	Stack,
	Text,
} from "@chakra-ui/react";

interface HomeProps {
	readonly isAuthenticated: boolean;
	readonly onOpenLogin: () => void;
	readonly onOpenSearch: () => void;
}

const references = [
	{
		title: "Institutional Landing",
		source: "/design/landpage_example.png",
	},
	{
		title: "Map Search",
		source: "/design/instructor_search_mapview_example.png",
	},
	{
		title: "Instructor Dashboard",
		source: "/design/instructor_dashboard_example.png",
	},
	{
		title: "Administrative Panel",
		source: "/design/admin_dashboard_example.png",
	},
];

const highlights = [
	{
		title: "Geolocation Search",
		description:
			"Find certified instructors by neighborhood, distance, and specialty.",
		icon: Compass,
	},
	{
		title: "Profile Governance",
		description:
			"Administrative approval flow to maintain quality and safety on the platform.",
		icon: ShieldCheck,
	},
	{
		title: "Scheduling Rules",
		description:
			"Booking with a minimum of 2 consecutive hours and status timeline for each reservation.",
		icon: TimerReset,
	},
];

export default function Home({
isAuthenticated,
onOpenLogin,
onOpenSearch,
}: HomeProps) {
	return (
<Stack minH="100vh" pb={14}>
			<Container maxW="7xl" pt={{ base: 9, md: 14 }}>
				<Grid
					templateColumns={{ base: "1fr", lg: "1.15fr 0.85fr" }}
					gap={8}>
					<Stack gap={6}>
						<Box
							alignSelf="start"
							px={3}
							py={1}
							borderRadius="full"
							bg="brand.muted"
							color="brand.emphasized"
							fontSize="xs"
							fontWeight="700"
							letterSpacing="0.08em"
							textTransform="uppercase">
							LinkAuto • MVP v1
						</Box>

						<Stack gap={3.5}>
							<Heading
								fontSize={{ base: "3xl", md: "4xl" }}
								lineHeight="1.1"
								color="text.primary">
								Connect students and driving instructors with a
								clear, local, and reliable search.
							</Heading>
							<Text
								fontSize={{ base: "md", md: "lg" }}
								lineHeight="1.6"
								color="text.secondary"
								maxW="680px">
								The platform applies instructor validation,
								scheduling with slot rules, and status flow to
								provide predictability for both students and
								instructors.
							</Text>
						</Stack>

						<HStack gap={3} flexWrap="wrap">
							<Button
								h="48px"
								px={6}
								bg="brand.500"
								color="white"
								fontWeight="700"
								onClick={
									isAuthenticated ? onOpenSearch : onOpenLogin
								}
								_hover={{ bg: "brand.600" }}>
								{isAuthenticated
									? "Go to Search"
									: "Access Platform"}
								<ArrowRight size={16} />
							</Button>
							<Button
								h="48px"
								px={6}
								variant="outline"
								borderColor="border.default"
								color="text.secondary"
								onClick={onOpenSearch}>
								View Demo Search
							</Button>
						</HStack>

						<SimpleGrid columns={{ base: 1, md: 3 }} gap={3.5}>
							{highlights.map((item) => {
								const Icon = item.icon;
								return (
<Box
										key={item.title}
										bg="surface.panel"
										border="1px solid"
										borderColor="border.default"
										borderRadius="2xl"
										p={4}>
										<HStack gap={2.5} align="start">
											<Box
												w="34px"
												h="34px"
												borderRadius="lg"
												display="grid"
												placeItems="center"
												bg="accent.muted"
												color="accent.emphasized">
												<Icon
													size={18}
													aria-hidden="true"
												/>
											</Box>
											<Stack gap={1}>
												<Text
													fontWeight="700"
													color="text.primary">
													{item.title}
												</Text>
												<Text
													fontSize="sm"
													color="text.muted"
													lineHeight="1.5">
													{item.description}
												</Text>
											</Stack>
										</HStack>
									</Box>
								);
							})}
						</SimpleGrid>
					</Stack>

					<Box
						border="1px solid"
						borderColor="border.default"
						borderRadius="3xl"
						bg="surface.panel"
						p={4}
						boxShadow="0 28px 48px rgba(17, 24, 39, 0.08)">
						<Image
							src="/brand/LinkAuto-banner.webp"
							alt="LinkAuto Visual Identity"
							borderRadius="2xl"
							w="100%"
							objectFit="cover"
						/>
						<Text
							mt={3}
							fontSize="sm"
							color="text.muted"
							fontWeight="600">
							Design inspired by refined civic tech with a focus on
							readability, trust, and speed of action.
						</Text>
					</Box>
				</Grid>
			</Container>

			<Container maxW="7xl" pt={12}>
				<Stack gap={4}>
					<Heading
						fontSize={{ base: "xl", md: "2xl" }}
						color="text.primary">
						Visual references used in this delivery
					</Heading>
					<Text color="text.muted" maxW="720px">
						The compositions below were used as a guide for the
						landing page, search map, and dashboards, adapted for
						the user specification and scheduling flows.
					</Text>
				</Stack>

				<SimpleGrid mt={5} columns={{ base: 1, md: 2 }} gap={4}>
					{references.map((reference) => (
<Box
							key={reference.title}
							bg="surface.panel"
							border="1px solid"
							borderColor="border.default"
							borderRadius="2xl"
							overflow="hidden">
							<Image
								src={reference.source}
								alt={reference.title}
								w="100%"
								h="220px"
								objectFit="cover"
							/>
							<Text
								px={4}
								py={3}
								fontWeight="700"
								color="text.primary">
								{reference.title}
							</Text>
						</Box>
					))}
				</SimpleGrid>
			</Container>
		</Stack>
	);
}
