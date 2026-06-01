import { useState } from "react";
import {
	Box,
	Button,
	Flex,
	Heading,
	Input,
	Stack,
	Text,
	HStack,
} from "@chakra-ui/react";
import { Link as RouterLink } from "react-router-dom";
import { CheckCircle, AlertTriangle } from "lucide-react";
import { httpClient } from "../services/httpClient";

export default function PasswordReset() {
	const [email, setEmail] = useState("");
	const [submitting, setSubmitting] = useState(false);
	const [successMsg, setSuccessMsg] = useState<string | null>(null);
	const [errorMsg, setErrorMsg] = useState<string | null>(null);

	const handleResetRequest = async (e: React.FormEvent) => {
		e.preventDefault();
		if (!email.trim()) return;

		setSubmitting(true);
		setSuccessMsg(null);
		setErrorMsg(null);

		try {
			// Envia a requisição de reset para o backend
			await httpClient.post("/auth/password-reset", { email: email.trim() });
			setSuccessMsg("Se o email estiver cadastrado, você receberá instruções de recuperação.");
			setEmail("");
		} catch (err: unknown) {
			console.error("Error requesting password reset:", err);
			const msg = err instanceof Error ? err.message : "Erro ao solicitar recuperação de senha. Tente novamente.";
			setErrorMsg(msg);
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
			{/* Formulário de Recuperação */}
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
							fontWeight="800"
							lineHeight="1.1"
							letterSpacing="tight"
							mb={3}>
							Esqueceu a senha?
						</Heading>
						<Text color="text.muted" fontSize="md">
							Insira seu e-mail cadastrado e enviaremos um link para você redefinir sua senha.
						</Text>
					</Box>

					{successMsg && (
						<HStack
							p={4}
							bg="green.50"
							color="green.700"
							borderRadius="xl"
							border="1px solid"
							borderColor="green.200"
							mb={6}
							gap={2}>
							<CheckCircle size={18} />
							<Text fontSize="sm" fontWeight="600">
								{successMsg}
							</Text>
						</HStack>
					)}

					{errorMsg && (
						<HStack
							p={4}
							bg="red.50"
							color="red.700"
							borderRadius="xl"
							border="1px solid"
							borderColor="red.200"
							mb={6}
							gap={2}>
							<AlertTriangle size={18} />
							<Text fontSize="sm" fontWeight="600">
								{errorMsg}
							</Text>
						</HStack>
					)}

					{!successMsg && (
						<form onSubmit={handleResetRequest}>
							<Stack gap={4}>
								<Box>
									<Text fontSize="xs" fontWeight="700" mb={1.5} color="text.secondary">
										Endereço de E-mail
									</Text>
									<Input
										type="email"
										required
										value={email}
										onChange={(e) => setEmail(e.target.value)}
										placeholder="seu.email@exemplo.com"
										color="text.primary"
										bg="surface.canvas"
										h="48px"
										borderRadius="xl"
									/>
								</Box>

								<Button
									type="submit"
									h="48px"
									bg="brand.solid"
									color="text.inverse"
									fontSize="sm"
									fontWeight="bold"
									borderRadius="xl"
									loading={submitting}
									_hover={{ bg: "brand.emphasized" }}>
									Enviar link de recuperação
								</Button>
							</Stack>
						</form>
					)}

					<Box mt={6} textAlign="center">
						<Text color="text.muted" fontSize="sm">
							Lembrou a senha?{" "}
							<RouterLink to="/login">
								<Text
									as="span"
									color="brand.solid"
									fontWeight="bold"
									textDecoration="underline"
									cursor="pointer"
									_hover={{ color: "brand.emphasized" }}>
									Fazer login
								</Text>
							</RouterLink>
						</Text>
					</Box>
				</Box>
			</Flex>

			{/* Painel Informativo Lateral */}
			<Flex
				flex={1}
				bgGradient="linear(to-br, #0f2f47, #1f5b86)"
				align="center"
				justify="center"
				position="relative"
				display={{ base: "none", lg: "flex" }}>
				<Box maxW="450px" textAlign="center" color="white" px={8} zIndex={1}>
					<Heading fontSize="4xl" fontWeight="950" mb={4}>
						Segurança em primeiro lugar.
					</Heading>
					<Text fontSize="lg" opacity={0.9} fontWeight="500">
						Garantimos a proteção de todas as suas informações de acesso com segurança ponta a ponta.
					</Text>
				</Box>
			</Flex>
		</Flex>
	);
}
