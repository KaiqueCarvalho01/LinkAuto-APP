import { useEffect, useState } from "react";
import { Box, Button, Flex, Heading, HStack, Input, Stack, Text } from "@chakra-ui/react";
import { Link as RouterLink, useSearchParams } from "react-router-dom";
import { AlertTriangle, CheckCircle } from "lucide-react";
import { httpClient } from "../services/httpClient";

const MIN_PASSWORD_LENGTH = 8;

export default function PasswordResetConfirm() {
	const [searchParams, setSearchParams] = useSearchParams();
	// Keep the token in memory only: remove it from the address bar and browser history
	const [token] = useState(() => searchParams.get("token") ?? "");
	useEffect(() => {
		if (searchParams.has("token")) {
			setSearchParams({}, { replace: true });
		}
	}, [searchParams, setSearchParams]);
	const [password, setPassword] = useState("");
	const [confirmation, setConfirmation] = useState("");
	const [submitting, setSubmitting] = useState(false);
	const [done, setDone] = useState(false);
	const [errorMsg, setErrorMsg] = useState<string | null>(
		token ? null : "Link de redefinição inválido. Solicite um novo link.",
	);

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault();
		if (password.length < MIN_PASSWORD_LENGTH) {
			setErrorMsg(`A senha deve ter pelo menos ${MIN_PASSWORD_LENGTH} caracteres.`);
			return;
		}
		if (password !== confirmation) {
			setErrorMsg("As senhas não coincidem.");
			return;
		}

		setSubmitting(true);
		setErrorMsg(null);
		try {
			await httpClient.post("/auth/password-reset/confirm", {
				token,
				new_password: password,
			});
			setDone(true);
		} catch (err: unknown) {
			console.error("Error confirming password reset:", err);
			setErrorMsg(
				"Este link é inválido, já foi usado ou expirou. Solicite um novo link.",
			);
		} finally {
			setSubmitting(false);
		}
	};

	return (
		<Flex minH="100vh" w="full" align="center" justify="center" bg="surface.canvas" px={6}>
			<Box w="full" maxW="400px" bg="surface.panel" p={{ base: 6, md: 10 }} borderRadius="2xl">
				<Heading color="text.primary" fontSize="3xl" fontWeight="800" mb={3}>
					Nova senha
				</Heading>
				<Text color="text.muted" fontSize="md" mb={8}>
					Escolha uma nova senha para sua conta. Por segurança, você será
					desconectado de todos os dispositivos.
				</Text>

				{done && (
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
							Senha alterada com sucesso. Entre com a nova senha.
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

				{!done && token && (
					<form onSubmit={handleSubmit}>
						<Stack gap={4}>
							<Box>
								<Text
									asChild
									display="block"
									fontSize="xs"
									fontWeight="700"
									mb={1.5}
									color="text.secondary">
									<label htmlFor="new-password">Nova senha</label>
								</Text>
								<Input
									id="new-password"
									type="password"
									autoComplete="new-password"
									required
									minLength={MIN_PASSWORD_LENGTH}
									value={password}
									onChange={(e) => setPassword(e.target.value)}
									color="text.primary"
									bg="surface.canvas"
									h="48px"
									borderRadius="xl"
								/>
							</Box>
							<Box>
								<Text
									asChild
									display="block"
									fontSize="xs"
									fontWeight="700"
									mb={1.5}
									color="text.secondary">
									<label htmlFor="confirm-password">Confirme a nova senha</label>
								</Text>
								<Input
									id="confirm-password"
									type="password"
									autoComplete="new-password"
									required
									value={confirmation}
									onChange={(e) => setConfirmation(e.target.value)}
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
								Salvar nova senha
							</Button>
						</Stack>
					</form>
				)}

				<Box mt={6} textAlign="center">
					<RouterLink to={done ? "/login" : "/password-reset"}>
						<Text
							as="span"
							color="brand.solid"
							fontWeight="bold"
							textDecoration="underline"
							fontSize="sm">
							{done ? "Fazer login" : "Solicitar um novo link"}
						</Text>
					</RouterLink>
				</Box>
			</Box>
		</Flex>
	);
}
