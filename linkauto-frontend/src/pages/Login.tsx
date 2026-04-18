import { useState } from "react";
import {
	Box,
	Button,
	Flex,
	Heading,
	HStack,
	Input,
	Stack,
	Text,
	VStack,
} from "@chakra-ui/react";

import { BrandLockup } from "../components/BrandLockup";

type PreferredRole = "student" | "instructor";

interface LoginProps {
	readonly onAuthenticate: (payload: {
		email: string;
		password: string;
		preferredRole: PreferredRole;
	}) => Promise<void>;
}

export default function Login({ onAuthenticate }: LoginProps) {
	const [preferredRole, setPreferredRole] =
		useState<PreferredRole>("student");
	const [email, setEmail] = useState("");
	const [password, setPassword] = useState("");
	const [submitting, setSubmitting] = useState(false);
	const [errorMessage, setErrorMessage] = useState("");

	const submitAuthentication = async () => {
		if (!email || !password) {
			return;
		}

		setSubmitting(true);
		setErrorMessage("");
		try {
			await onAuthenticate({ email, password, preferredRole });
		} catch (error) {
			const fallback = "Nao foi possivel autenticar sua conta.";
			if (error instanceof Error) {
				setErrorMessage(error.message || fallback);
			} else {
				setErrorMessage(fallback);
			}
		} finally {
			setSubmitting(false);
		}
	};

	return (
		<Flex
			minH="100vh"
			position="relative"
			px={{ base: 5, md: 8 }}
			py={{ base: 8, md: 12 }}
			justify="center"
			align="center"
			overflow="hidden">
			<Box
				position="absolute"
				top="-120px"
				left="-120px"
				w="320px"
				h="320px"
				borderRadius="full"
				bg="brand.200"
				filter="blur(70px)"
				opacity={0.55}
			/>
			<Box
				position="absolute"
				bottom="-140px"
				right="-100px"
				w="360px"
				h="360px"
				borderRadius="full"
				bg="accent.200"
				filter="blur(80px)"
				opacity={0.45}
			/>

			<Flex
				w="full"
				maxW="1080px"
				direction={{ base: "column", lg: "row" }}
				bg="surface.panel"
				borderRadius={{ base: "3xl", lg: "32px" }}
				boxShadow="0 30px 80px rgba(19, 62, 93, 0.18)"
				overflow="hidden"
				border="1px solid"
				borderColor="white">
				<Box
					position="relative"
					flex={{ base: "0 0 auto", lg: "0 0 44%" }}
					minH={{ base: "280px", lg: "620px" }}
					p={{ base: 8, md: 10 }}
					bgGradient="linear(145deg, #0f2f47 0%, #236ea8 52%, #44ad4f 100%)"
					color="white">
					<Box
						position="absolute"
						inset="16px"
						borderRadius="28px"
						border="1px solid"
						borderColor="whiteAlpha.300"
						pointerEvents="none"
					/>

					<VStack
						align="start"
						justify="space-between"
						h="full"
						position="relative"
						zIndex={1}>
						<BrandLockup showTagline colorMode="dark" />
						<Stack gap={4} maxW="320px">
							<Text
								fontSize="xs"
								fontWeight="700"
								letterSpacing="0.18em"
								textTransform="uppercase"
								color="whiteAlpha.700">
								Fatec Mogi Mirim • ADS 2026
							</Text>
							<Heading
								fontFamily="heading"
								fontSize={{ base: "2xl", md: "3xl" }}
								lineHeight="1.08">
								Projeto comercial com qualidade enterprise e
								foco jovem.
							</Heading>
							<Text color="whiteAlpha.800" fontWeight="500">
								Agendamento inteligente de instrutores
								autonomos, com governanca de perfis e fluxo
								integrado ao backend LinkAuto.
							</Text>
						</Stack>
					</VStack>
				</Box>

				<Box flex="1" p={{ base: 7, md: 10 }}>
					<Stack
						gap={7}
						maxW="420px"
						mx="auto"
						justify="center"
						h="full">
						<Stack gap={2}>
							<Heading
								fontFamily="heading"
								fontSize={{ base: "2xl", md: "3xl" }}
								color="ink.900">
								Bem-vindo ao painel LinkAuto
							</Heading>
							<Text color="ink.500" fontWeight="500">
								Entre com seu e-mail institucional para acessar
								o fluxo de autenticacao.
							</Text>
						</Stack>

						<HStack
							bg="ink.50"
							p={1.5}
							borderRadius="xl"
							border="1px solid"
							borderColor="ink.100">
							<Button
								flex="1"
								h="44px"
								variant={
									preferredRole === "student"
										? "solid"
										: "ghost"
								}
								bg={
									preferredRole === "student"
										? "brand.600"
										: "transparent"
								}
								color={
									preferredRole === "student"
										? "white"
										: "ink.600"
								}
								onClick={() => setPreferredRole("student")}
								borderRadius="lg">
								Aluno
							</Button>
							<Button
								flex="1"
								h="44px"
								variant={
									preferredRole === "instructor"
										? "solid"
										: "ghost"
								}
								bg={
									preferredRole === "instructor"
										? "brand.600"
										: "transparent"
								}
								color={
									preferredRole === "instructor"
										? "white"
										: "ink.600"
								}
								onClick={() => setPreferredRole("instructor")}
								borderRadius="lg">
								Instrutor
							</Button>
						</HStack>

						<Box
							as="form"
							onSubmit={(event) => {
								event.preventDefault();
								void submitAuthentication();
							}}>
							<Stack gap={4}>
								<Box>
									<Box
										as="label"
										display="block"
										fontWeight="700"
										fontSize="sm"
										mb={1.5}>
										E-mail
									</Box>
									<Input
										id="email"
										type="email"
										aria-label="E-mail"
										value={email}
										onChange={(event) =>
											setEmail(event.target.value)
										}
										h="50px"
										bg="white"
										borderColor="ink.200"
										placeholder="voce@linkauto.app"
										required
										_focusVisible={{
											borderColor: "brand.500",
											boxShadow: "0 0 0 1px #49abf4",
										}}
									/>
								</Box>

								<Box>
									<Flex
										justify="space-between"
										align="center"
										mb={1.5}>
										<Box
											as="span"
											fontWeight="700"
											fontSize="sm">
											Senha
										</Box>
										<Text
											fontSize="xs"
											fontWeight="700"
											color="brand.600">
											Recuperar acesso
										</Text>
									</Flex>
									<Input
										id="password"
										type="password"
										aria-label="Senha"
										value={password}
										onChange={(event) =>
											setPassword(event.target.value)
										}
										h="50px"
										bg="white"
										borderColor="ink.200"
										placeholder="••••••••"
										required
										_focusVisible={{
											borderColor: "brand.500",
											boxShadow: "0 0 0 1px #49abf4",
										}}
									/>
								</Box>

								<Button
									type="submit"
									h="52px"
									bgGradient="linear(95deg, brand.700, brand.500)"
									color="white"
									fontWeight="800"
									loading={submitting}
									loadingText="Entrando"
									_hover={{ filter: "brightness(1.05)" }}>
									Entrar no LinkAuto
								</Button>

								{errorMessage ? (
									<Box
										px={4}
										py={3}
										borderRadius="lg"
										bg="#fff0f0"
										border="1px solid"
										borderColor="#ffc9c9">
										<Text
											fontSize="sm"
											color="#c92a2a"
											fontWeight="700">
											{errorMessage}
										</Text>
									</Box>
								) : null}
							</Stack>
						</Box>
					</Stack>
				</Box>
			</Flex>
		</Flex>
	);
}
