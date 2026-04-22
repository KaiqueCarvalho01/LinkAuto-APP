import {
	Box,
	Container,
	SimpleGrid,
	Stack,
	Text,
	Link,
} from "@chakra-ui/react";
import { Link as RouterLink } from "react-router-dom";
import { BrandLockup } from "./BrandLockup";

const ListHeader = ({ children }: { children: React.ReactNode }) => {
	return (
<Text fontWeight="bold" fontSize="lg" mb={2} color="text.primary">
			{children}
		</Text>
	);
};

export function Footer() {
	return (
<Box
			as="footer"
			role="contentinfo"
			bg="surface.panel"
			color="text.muted"
			borderTop="1px solid"
			borderColor="border.subtle"
			py={12}>
			<Container maxW="container.xl">
				<SimpleGrid
					templateColumns={{ base: "1fr", md: "2fr 1fr 1fr 1fr" }}
					gap={8}>
					<Stack gap={6}>
						<BrandLockup />
						<Text fontSize="sm">
							LinkAuto is the leading platform for connecting
							driving instructors and students. We make the
							process of learning to drive simpler, safer, and
							more transparent.
						</Text>
						<Text fontSize="sm">
							© 2026 LinkAuto. All rights reserved.
						</Text>
					</Stack>

					<Stack align="flex-start" gap={3}>
						<ListHeader>Students</ListHeader>
						<Link asChild variant="plain" color="inherit" _hover={{ color: "brand.500" }}>
							<RouterLink to="/students/first-license">
								First License
							</RouterLink>
						</Link>
						<Link asChild variant="plain" color="inherit" _hover={{ color: "brand.500" }}>
							<RouterLink to="/search">
								Find an Instructor
							</RouterLink>
						</Link>
						<Link asChild variant="plain" color="inherit" _hover={{ color: "brand.500" }}>
							<RouterLink to="/student/lessons">
								My Lessons
							</RouterLink>
						</Link>
					</Stack>

					<Stack align="flex-start" gap={3}>
						<ListHeader>Instructors</ListHeader>
						<Link asChild variant="plain" color="inherit" _hover={{ color: "brand.500" }}>
							<RouterLink to="/instructors/register">
								Register as Instructor
							</RouterLink>
						</Link>
						<Link asChild variant="plain" color="inherit" _hover={{ color: "brand.500" }}>
							<RouterLink to="/instructor/students">
								My Students
							</RouterLink>
						</Link>
						<Link asChild variant="plain" color="inherit" _hover={{ color: "brand.500" }}>
							<RouterLink to="/instructor/vehicles">
								My Vehicles
							</RouterLink>
						</Link>
					</Stack>

					<Stack align="flex-start" gap={3}>
						<ListHeader>Institutional</ListHeader>
						<Link asChild variant="plain" color="inherit" _hover={{ color: "brand.500" }}>
							<RouterLink to="/about">About Us</RouterLink>
						</Link>
						<Link asChild variant="plain" color="inherit" _hover={{ color: "brand.500" }}>
							<RouterLink to="/contact">Contact</RouterLink>
						</Link>
						<Link asChild variant="plain" color="inherit" _hover={{ color: "brand.500" }}>
							<RouterLink to="/terms">Terms of Service</RouterLink>
						</Link>
					</Stack>
				</SimpleGrid>
			</Container>
		</Box>
	);
}
