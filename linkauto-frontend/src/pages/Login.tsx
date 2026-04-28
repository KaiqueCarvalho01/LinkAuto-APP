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
	Separator,
	Checkbox,
	CheckboxHiddenInput,
	Field,
} from "@chakra-ui/react";
import { Link as RouterLink } from "react-router-dom";

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
			bg="surface.canvas">
			{/* =========================================
          LADO ESQUERDO: Formulário de Login
          ========================================= */}
			<Flex
				flex={{ base: 1, lg: "0 0 45%" }}
				align="center"
				justify="center"
				px={{ base: 6, md: 10 }}
				py={{ base: 10, md: 12 }}
				bg="surface.panel">
				<Box w="full" maxW="400px">
					{/* Botão de Voltar */}
					<Box mb={10}>
						<RouterLink to="/">
							<Text
								as="span"
								color="text.muted"
								fontSize="sm"
								cursor="pointer"
								_hover={{ color: "brand.solid" }}>
								&lt; Voltar para{" "}
								<Text
									as="span"
									textDecoration="underline"
									color="brand.solid"
									fontWeight="bold">
									LinkAuto
								</Text>
							</Text>
						</RouterLink>
					</Box>

					<Box mb={8}>
						<Heading
							color="text.primary"
							fontSize="4xl"
							fontWeight="bold"
							mb={2}
							letterSpacing="tight">
							Entrar
						</Heading>
						<Text color="text.secondary" fontSize="md">
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
						<HStack bg="surface.muted" p={1} borderRadius="xl">
							<Button
								flex="1"
								h="44px"
								type="button"
								variant={
									preferredRole === "student"
										? "solid"
										: "ghost"
								}
								bg={
									preferredRole === "student"
										? "brand.solid"
										: "transparent"
								}
								color={
									preferredRole === "student"
										? "text.inverse"
										: "text.secondary"
								}
								onClick={() => setPreferredRole("student")}
								borderRadius="lg"
								_hover={
									preferredRole === "student"
										? {}
										: { bg: "whiteAlpha.200" }
								}>
								Aluno
							</Button>
							<Button
								flex="1"
								h="44px"
								type="button"
								variant={
									preferredRole === "instructor"
										? "solid"
										: "ghost"
								}
								bg={
									preferredRole === "instructor"
										? "brand.solid"
										: "transparent"
								}
								color={
									preferredRole === "instructor"
										? "text.inverse"
										: "text.secondary"
								}
								onClick={() => setPreferredRole("instructor")}
								borderRadius="lg"
								_hover={
									preferredRole === "instructor"
										? {}
										: { bg: "whiteAlpha.200" }
								}>
								Instrutor
							</Button>
						</HStack>

						<HStack w="full" my={2}>
							<Separator borderColor="border.subtle" />
							<Text
								fontSize="sm"
								color="text.muted"
								whiteSpace="nowrap"></Text>
							<Separator borderColor="border.subtle" />
						</HStack>

						{/* Input de E-mail */}
						<Field.Root id="email" required>
							<Field.Label fontWeight="bold">E-mail</Field.Label>
							<Input
								type="email"
								value={email}
								onChange={(e) => setEmail(e.target.value)}
								placeholder="voce@linkauto.app"
								h="54px"
								borderRadius="xl"
								borderColor="border.default"
								bg="surface.panel"
								_focusVisible={{
									borderColor: "brand.solid",
									boxShadow:
										"0 0 0 1px var(--chakra-colors-brand-solid)",
								}}
							/>
						</Field.Root>

						{/* Input de Senha */}
						<Field.Root id="password" required>
							<Field.Label fontWeight="bold">Senha</Field.Label>
							<Input
								type="password"
								value={password}
								onChange={(e) => setPassword(e.target.value)}
								placeholder="Mín. 8 caracteres"
								h="54px"
								borderRadius="xl"
								borderColor="border.default"
								bg="surface.panel"
								_focusVisible={{
									borderColor: "brand.solid",
									boxShadow:
										"0 0 0 1px var(--chakra-colors-brand-solid)",
								}}
							/>
						</Field.Root>

						{/* Manter conectado e Esqueci a senha */}
						<HStack justify="space-between" mt={1}>
							<Checkbox.Root
								colorPalette="brand"
								size="md"
								value="remember-me">
								<CheckboxHiddenInput />
								<Checkbox.Control />
								<Checkbox.Label
									color="text.secondary"
									fontSize="sm">
									Manter conectado
								</Checkbox.Label>
							</Checkbox.Root>
							<Link asChild>
								<RouterLink to="#">
									<Text
										as="span"
										fontSize="sm"
										color="brand.solid"
										fontWeight="bold"
										_hover={{
											textDecoration: "underline",
										}}>
										Esqueceu a senha?
									</Text>
								</RouterLink>
							</Link>
						</HStack>

						{/* Mensagem de Erro */}
						{errorMessage && (
							<Box
								p={4}
								borderRadius="xl"
								bg="state.danger.bg"
								border="1px solid"
								borderColor="state.danger.border">
								<Text
									fontSize="sm"
									color="state.danger.fg"
									fontWeight="medium">
									{errorMessage}
								</Text>
							</Box>
						)}

						{/* Botão de Submit */}
						<Button
							type="submit"
							h="54px"
							w="full"
							bg="brand.solid"
							color="text.inverse"
							fontWeight="bold"
							borderRadius="xl"
							loading={submitting}
							loadingText="Entrando"
							_hover={{ bg: "brand.emphasized" }}
							mt={2}
							shadow="0 10px 20px -5px var(--colors-brand-solid)">
							Entrar no LinkAuto
						</Button>

						<Text
							textAlign="center"
							fontSize="sm"
							color="text.muted"
							mt={4}>
							Ainda não registrado?{" "}
							<Text
								as="span"
								color="brand.solid"
								fontWeight="bold"
								cursor="pointer">
								<Link asChild colorPalette="brand">
									<RouterLink to="/register">
										Crie uma conta
									</RouterLink>
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
				flex="1"
				position="relative"
				p={{ lg: 8, xl: 10 }}
				align="center"
				justify="center"
				bg="surface.canvas">
				<Box
					borderRadius="3xl"
					w="full"
					h="full"
					overflow="hidden"
					position="relative"
					shadow="2xl">
					<Image
						src="/login_image.webp"
						alt="Ilustração ou Logo da LinkAuto"
						w="full"
						h="full"
						fit="cover"
					/>
					{/* Overlay Gradient */}
					<Box
						position="absolute"
						inset={0}
						bgGradient="to-t"
						gradientFrom="blackAlpha.800"
						gradientTo="transparent"
					/>

					<Stack
						position="absolute"
						bottom={12}
						left={12}
						gap={2}
						color="white">
						<Heading fontSize="3xl" fontWeight="800">
							Sua jornada começa aqui.
						</Heading>
						<Text fontSize="lg" opacity={0.9}>
							Acesse a maior rede de instrutores do país.
						</Text>
					</Stack>
				</Box>

				{/* Rodapé do Banner */}
				<HStack
					position="absolute"
					top={12}
					right={20}
					gap={6}
					fontSize="xs"
					fontWeight="bold"
					color="text.muted">
					<Link
						asChild
						variant="plain"
						_hover={{ color: "brand.solid" }}>
						<RouterLink to="/about">Sobre</RouterLink>
					</Link>
					<Link
						asChild
						variant="plain"
						_hover={{ color: "brand.solid" }}>
						<RouterLink to="/contact">Contato</RouterLink>
					</Link>
					<Link
						asChild
						variant="plain"
						_hover={{ color: "brand.solid" }}>
						<RouterLink to="/terms">Termos de Uso</RouterLink>
					</Link>
				</HStack>
			</Flex>
		</Flex>
	);
}
