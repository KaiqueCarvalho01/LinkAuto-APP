import {
	Box,
	Flex,
	HStack,
	Button,
	IconButton,
	MenuRoot,
	MenuTrigger,
	MenuContent,
	MenuItem,
} from "@chakra-ui/react";
import { Link as RouterLink } from "react-router-dom";
import { Menu, ChevronDown } from "lucide-react";
import { BrandLockup } from "./BrandLockup";
import { useState, useEffect } from "react";

export function Navbar() {
	const [scrolled, setScrolled] = useState(false);

	useEffect(() => {
		const handleScroll = () => {
			setScrolled(window.scrollY > 10);
		};
		window.addEventListener("scroll", handleScroll);
		return () => window.removeEventListener("scroll", handleScroll);
	}, []);

	return (
		<Box
			as="nav"
			position="fixed"
			top={0}
			w="full"
			zIndex={100}
			h={16}
			bg={scrolled ? "surface.panel" : "transparent"}
			backdropFilter={scrolled ? "blur(12px)" : "none"}
			borderBottom={scrolled ? "1px solid" : "none"}
			borderColor="border.subtle"
			transition="all 0.3s ease-in-out"
			boxShadow={
				scrolled ? "0 4px 20px -2px rgba(0, 0, 0, 0.05)" : "none"
			}>
			<Flex
				h={16}
				alignItems="center"
				justifyContent="space-between"
				maxW="container.xl"
				mx="auto"
				px={{ base: 4, md: 8 }}>
				<BrandLockup compact />

				{/* Desktop Menu */}
				<HStack gap={8} display={{ base: "none", lg: "flex" }}>
					<Button
						asChild
						variant="ghost"
						fontWeight="medium"
						color="text.primary"
						_hover={{ bg: "surface.muted" }}>
						<RouterLink to="/">Explore</RouterLink>
					</Button>

					<MenuRoot>
						<MenuTrigger asChild>
							<Button
								variant="ghost"
								fontWeight="medium"
								color="text.primary"
								_hover={{ bg: "surface.muted" }}>
								For Students <ChevronDown size={16} />
							</Button>
						</MenuTrigger>
						<MenuContent
							minW="220px"
							rounded="xl"
							shadow="md"
							p={2}>
							<MenuItem
								value="first-license"
								cursor="pointer"
								rounded="md"
								asChild>
								<RouterLink to="/students/first-license">
									First License
								</RouterLink>
							</MenuItem>
							<MenuItem
								value="licensed"
								cursor="pointer"
								rounded="md"
								asChild>
								<RouterLink to="/students/licensed">
									Licensed Drivers
								</RouterLink>
							</MenuItem>
							<MenuItem
								value="how-it-works"
								cursor="pointer"
								rounded="md"
								asChild>
								<RouterLink to="/students/how-it-works">
									How it Works
								</RouterLink>
							</MenuItem>
							<MenuItem
								value="search"
								color="brand.600"
								fontWeight="bold"
								cursor="pointer"
								rounded="md"
								asChild>
								<RouterLink to="/search">
									Find Instructors
								</RouterLink>
							</MenuItem>
						</MenuContent>
					</MenuRoot>

					<MenuRoot>
						<MenuTrigger asChild>
							<Button
								variant="ghost"
								fontWeight="medium"
								color="text.primary"
								_hover={{ bg: "surface.muted" }}>
								For Instructors <ChevronDown size={16} />
							</Button>
						</MenuTrigger>
						<MenuContent
							minW="220px"
							rounded="xl"
							shadow="md"
							p={2}>
							<MenuItem
								value="register"
								color="brand.600"
								fontWeight="bold"
								cursor="pointer"
								rounded="md"
								asChild>
								<RouterLink to="/instructors/register">
									Register Now
								</RouterLink>
							</MenuItem>
							<MenuItem
								value="how-it-works"
								cursor="pointer"
								rounded="md"
								asChild>
								<RouterLink to="/instructors/how-it-works">
									How it Works
								</RouterLink>
							</MenuItem>
							<MenuItem
								value="benefits"
								cursor="pointer"
								rounded="md"
								asChild>
								<RouterLink to="/instructors/benefits">
									Benefits
								</RouterLink>
							</MenuItem>
							<MenuItem
								value="simulator"
								cursor="pointer"
								rounded="md"
								asChild>
								<RouterLink to="/instructors/simulator">
									Simulator
								</RouterLink>
							</MenuItem>
						</MenuContent>
					</MenuRoot>

					<Button
						asChild
						variant="ghost"
						fontWeight="medium"
						color="text.primary"
						_hover={{ bg: "surface.muted" }}>
						<RouterLink to="/about">About</RouterLink>
					</Button>
					<Button
						asChild
						variant="ghost"
						fontWeight="medium"
						color="text.primary"
						_hover={{ bg: "surface.muted" }}>
						<RouterLink to="/contact">Contact</RouterLink>
					</Button>
				</HStack>

				{/* Desktop CTAs */}
				<HStack gap={4} display={{ base: "none", lg: "flex" }}>
					<Button
						asChild
						variant="ghost"
						fontWeight="bold"
						color="text.primary">
						<RouterLink to="/login">Log In</RouterLink>
					</Button>
					<Button
						asChild
						bg="brand.500"
						color="white"
						px={6}
						fontWeight="bold"
						_hover={{ bg: "brand.600" }}>
						<RouterLink to="/register">Sign Up</RouterLink>
					</Button>
				</HStack>

				{/* Mobile Menu Toggle */}
				<IconButton
					display={{ base: "flex", lg: "none" }}
					variant="ghost"
					aria-label="Open menu"
					color="text.primary">
					<Menu />
				</IconButton>
			</Flex>
		</Box>
	);
}
