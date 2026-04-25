import {
	Box,
	Container,
	Heading,
	Stack,
	Text,
	AccordionRoot,
	AccordionItem,
	AccordionItemTrigger,
	AccordionItemContent,
} from "@chakra-ui/react";

export function FAQ() {
	const items = [
		{
			value: "payment",
			title: "Como pago as aulas?",
			text: "Você pode pagar suas aulas diretamente pela plataforma usando cartão de crédito ou PIX. O valor fica retido com segurança e só é liberado para o instrutor após a conclusão da aula.",
		},
		{
			value: "cancellation",
			title: "Posso cancelar um agendamento?",
			text: "Sim, cancelamentos realizados com até 24h de antecedência garantem reembolso integral. Após esse período, uma taxa de conveniência pode ser aplicada.",
		},
		{
			value: "security",
			title: "É seguro ter aulas com instrutores da plataforma?",
			text: "Absolutamente. Todos os instrutores passam por uma rigorosa verificação de antecedentes, validação de documentos junto ao DETRAN e acompanhamento constante da qualidade.",
		},
		{
			value: "equipment",
			title: "Preciso ter meu próprio veículo?",
			text: "Não necessariamente. Muitos instrutores oferecem o veículo para as aulas. Você pode filtrar sua busca por instrutores que fornecem carro ou moto próprios.",
		},
	];

	return (
		<Box py={24} bg="bg.canvas">
			<Container maxW="container.md">
				<Stack gap={12}>
					<Stack textAlign="center" gap={4}>
						<Heading fontSize="3xl" fontWeight="800">
							Perguntas Frequentes
						</Heading>
						<Text color="text.muted" fontSize="lg">
							Tire suas dúvidas rápidas sobre como a LinkAuto funciona.
						</Text>
					</Stack>

					<AccordionRoot collapsible variant="subtle" size="lg">
						{items.map((item) => (
							<AccordionItem key={item.value} value={item.value} borderBottomWidth="1px" borderColor="border.subtle" py={2}>
								<AccordionItemTrigger fontWeight="bold">
									{item.title}
								</AccordionItemTrigger>
								<AccordionItemContent color="text.muted" pb={4}>
									{item.text}
								</AccordionItemContent>
							</AccordionItem>
						))}
					</AccordionRoot>
				</Stack>
			</Container>
		</Box>
	);
}
