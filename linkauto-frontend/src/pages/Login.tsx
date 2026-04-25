import { useState } from "react";
import {
	Box,
	Button,
	Flex,
	Heading,
	HStack,
	Input,
	Image,
	Link,
	Stack,
	Text,
	VStack,
	Separator,
	Checkbox,
	CheckboxHiddenInput,
} from "@chakra-ui/react";

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
			const fallback = "Não foi possível autenticar sua conta.";
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
			w="full"
			direction={{ base: "column", lg: "row" }}
			bg="white">
			{/* =========================================
          LADO ESQUERDO: Formulário de Login
          ========================================= */}
			<Flex
				flex={{ base: 1, lg: "0 0 40%" }}
				align="center"
				justify="center"
				px={{ base: 6, md: 10 }}
				py={{ base: 10, md: 12 }}>
				<Box w="full" maxW="420px">
					{/* Botão de Voltar (opcional) */}
					<Text
						color="gray.500"
						fontSize="sm"
						mb={10}
						cursor="pointer"
						_hover={{ color: "brand.500" }}>
						&lt; Voltar para{" "}
						<Link variant="underline" href="/" colorPalette="brand">
							LinkAuto
						</Link>
					</Text>

					<Box mb={8}>
						<Heading
							color="brand.900"
							fontSize="4xl"
							fontWeight="bold"
							mb={2}>
							Entrar
						</Heading>
						<Text color="gray.500" fontSize="md">
							Insira seu e-mail e senha para acessar sua conta!
						</Text>
					</Box>

					<Stack
						as="form"
						gap={5}
						onSubmit={(event) => {
							event.preventDefault();
							void submitAuthentication();
						}}>
						{/* Seletor de Perfil */}
						<HStack bg="gray.50" p={1} borderRadius="xl">
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
										? "brand.500"
										: "transparent"
								}
								color={
									preferredRole === "student"
										? "white"
										: "gray.600"
								}
								onClick={() => setPreferredRole("student")}
								borderRadius="lg"
								_hover={
									preferredRole === "student"
										? {}
										: { bg: "gray.200" }
								}>
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
										? "brand.500"
										: "transparent"
								}
								color={
									preferredRole === "instructor"
										? "white"
										: "gray.600"
								}
								onClick={() => setPreferredRole("instructor")}
								borderRadius="lg"
								_hover={
									preferredRole === "instructor"
										? {}
										: { bg: "gray.200" }
								}>
								Instrutor
							</Button>
						</HStack>

						<HStack w="full" my={2}>
							<Separator borderColor="gray.300" />
							<Text
								fontSize="sm"
								color="gray.400"
								whiteSpace="nowrap"></Text>
							<Separator borderColor="gray.300" />
						</HStack>

						{/* Input de E-mail */}
						<Box>
							<Text
								as="label"
								display="block"
								fontSize="sm"
								fontWeight="medium"
								color="gray.700"
								mb={2}>
								E-mail*
							</Text>
							<Input
								id="email"
								type="email"
								value={email}
								onChange={(e) => setEmail(e.target.value)}
								placeholder="voce@linkauto.app"
								h="50px"
								borderRadius="xl"
								borderColor="gray.200"
								_focusVisible={{
									borderColor: "brand.500",
									boxShadow: "outline",
								}}
								required
							/>
						</Box>

						{/* Input de Senha */}
						<Box>
							<Text
								as="label"
								display="block"
								fontSize="sm"
								fontWeight="medium"
								color="gray.700"
								mb={2}>
								Senha*
							</Text>
							<Input
								id="password"
								type="password"
								value={password}
								onChange={(e) => setPassword(e.target.value)}
								placeholder="Mín. 8 caracteres"
								h="50px"
								borderRadius="xl"
								borderColor="gray.200"
								_focusVisible={{
									borderColor: "brand.500",
									boxShadow: "outline",
								}}
								required
							/>
						</Box>

						{/* Manter conectado e Esqueci a senha */}
						<HStack justify="space-between" mt={1}>
							<Checkbox.Root
								colorPalette="brand"
								size="md"
								value="remember-me">
								<CheckboxHiddenInput />
								<Checkbox.Control />
								<Checkbox.Label color="gray.600" fontSize="sm">
									Manter conectado
								</Checkbox.Label>
							</Checkbox.Root>
							<Link href="#">
								<Text
									as="a"
									fontSize="sm"
									color="brand.500"
									fontWeight="medium"
									_hover={{ textDecoration: "underline" }}>
									Esqueceu a senha?
								</Text>
							</Link>
						</HStack>
						{/* Mensagem de Erro */}
						{errorMessage && (
							<Box
								p={3}
								borderRadius="md"
								bg="red.50"
								border="1px solid"
								borderColor="red.200">
								<Text
									fontSize="sm"
									color="red.600"
									fontWeight="medium">
									{errorMessage}
								</Text>
							</Box>
						)}

						{/* Botão de Submit */}
						<Button
							type="submit"
							h="50px"
							w="full"
							bg="brand.500" // Use a cor azul/roxa vibrante do seu tema aqui
							color="white"
							fontWeight="bold"
							borderRadius="xl"
							loading={submitting}
							loadingText="Entrando"
							_hover={{ bg: "brand.600" }}
							mt={2}>
							Entrar no LinkAuto
						</Button>

						<Text
							textAlign="center"
							fontSize="sm"
							color="gray.600"
							mt={4}>
							Ainda não registrado?{" "}
							<Text
								as="span"
								color="brand.500"
								fontWeight="bold"
								cursor="pointer">
								<Link
									href="/register"
									variant="underline"
									colorPalette="brand">
									Crie uma conta
								</Link>
							</Text>
						</Text>
					</Stack>
				</Box>
			</Flex>

			{/* =========================================
          LADO DIREITO: Banner Visual
          ========================================= */}
			<Flex
				display={{ base: "none", lg: "flex" }}
				flex="1" // Garante que divida o espaço meio a meio com o formulário
				position="relative"
				p={{ lg: 8, xl: 10 }} // Cria a margem branca ao redor (efeito "card")
				align="center"
				justify="center">
				<Box
					borderRadius="3xl"
					w="full"
					h="full"
					overflow="hidden"
					position="relative">
					<Image
						src="/login_image.webp"
						alt="Ilustração ou Logo da LinkAuto"
						w="full"
						h="full"
						fit="cover"
					/>
					<Box
						border="1px solid"
						borderColor="whiteAlpha.400"
						bg="whiteAlpha.100"
						backdropFilter="blur(10px)"
						px={8}
						py={4}
						borderRadius="2xl"
						mt={8}></Box>
				</Box>

				{/* Rodapé do Banner */}
				<HStack
					position="absolute"
					bottom={2}
					right={{ lg: 8, xl: 10 }} // Alinha com o início do card
					gap={6}
					fontSize="sm"
					fontWeight="medium"
					color="gray.500">
					<Link variant="plain" href="/about">
						Sobre
					</Link>
					<Link variant="plain" href="/contact">
						Contato
					</Link>
					<Link variant="plain" href="/terms">
						Termos de Uso
					</Link>
					<Link variant="plain" href="">
						Blog
					</Link>
				</HStack>
			</Flex>
		</Flex>
	);
}
