import { useCallback, useEffect, useMemo, useState } from "react";
import { Search } from "lucide-react";
import {
	Box,
	Button,
	chakra,
	Container,
	Grid,
	Heading,
	HStack,
	Input,
	SimpleGrid,
	Skeleton,
	Stack,
	Text,
} from "@chakra-ui/react";

import { BrandLockup } from "../components/BrandLockup";
import { InstructorCard } from "../components/InstructorCard";
import { InstructorMap } from "../components/InstructorMap";
import { searchInstructors } from "../services/instructorSearch";
import { mockInstructors } from "../services/mockData";
import type {
	InstructorSearchParams,
	InstructorSummary,
} from "../types/instructor";

interface SearchPageProps {
	readonly token: string | undefined;
	readonly onOpenProfile: () => void;
	readonly onStartBooking: (instructor: InstructorSummary) => void;
}

export default function SearchPage({
	token,
	onOpenProfile,
	onStartBooking,
}: SearchPageProps) {
	const [query, setQuery] = useState("");
	const [city, setCity] = useState("");
	const [specialty, setSpecialty] = useState("Todas");
	const [radiusKm, setRadiusKm] = useState(10);
	const [loading, setLoading] = useState(false);
	const [instructors, setInstructors] = useState<InstructorSummary[]>([]);
	const [selectedInstructorId, setSelectedInstructorId] = useState<string>();

	const specialties = useMemo(() => {
		const allSpecialties = mockInstructors.flatMap(
			(item) => item.specialties,
		);
		return ["Todas", ...new Set(allSpecialties)];
	}, []);

	const loadInstructors = useCallback(async () => {
		setLoading(true);
		const params: InstructorSearchParams = {
			query,
			city,
			specialty,
			radiusKm,
			minRating: 0,
		};

		try {
			const results = await searchInstructors(params, token);
			setInstructors(results);
			setSelectedInstructorId((current) => current ?? results[0]?.id);
		} finally {
			setLoading(false);
		}
	}, [city, query, radiusKm, specialty, token]);

	useEffect(() => {
		void loadInstructors();
	}, [loadInstructors]);

	const selectedInstructor =
		instructors.find((item) => item.id === selectedInstructorId) ??
		instructors[0] ??
		null;

	return (
		<Stack minH="100vh" pb={10}>
			<Box
				bg="surface.panel"
				borderBottom="1px solid"
				borderColor="border.default">
				<Container maxW="7xl" py={3.5}>
					<HStack justify="space-between">
						<BrandLockup compact />
						<HStack gap={2}>
							<Button
								variant="ghost"
								onClick={onOpenProfile}
								color="text.secondary">
								Meu perfil
							</Button>
						</HStack>
					</HStack>
				</Container>
			</Box>

			<Container maxW="7xl" pt={8}>
				<Stack gap={6}>
					<Stack gap={1.5}>
						<Heading
							fontSize={{ base: "2xl", md: "3xl" }}
							color="text.primary">
							Buscar instrutores disponiveis
						</Heading>
						<Text color="text.muted" maxW="760px">
							Encontre instrutores aprovados, compare avaliacao e
							selecione slots para iniciar seu agendamento de
							forma segura.
						</Text>
					</Stack>

					<SimpleGrid columns={{ base: 1, md: 2, lg: 5 }} gap={3}>
						<Box gridColumn={{ lg: "span 2" }}>
							<Input
								placeholder="Nome ou especialidade"
								value={query}
								onChange={(event) =>
									setQuery(event.target.value)
								}
								h="46px"
								bg="surface.panel"
								borderColor="border.default"
								color="text.primary"
							/>
						</Box>

						<Input
							placeholder="Cidade ou bairro"
							value={city}
							onChange={(event) => setCity(event.target.value)}
							h="46px"
							bg="surface.panel"
							borderColor="border.default"
							color="text.primary"
						/>

						<chakra.select
							value={specialty}
							onChange={(event) =>
								setSpecialty(event.target.value)
							}
							h="46px"
							borderRadius="md"
							border="1px solid"
							borderColor="border.default"
							bg="surface.panel"
							px={3}
							fontSize="sm"
							fontWeight="600"
							color="text.primary"
							aria-label="Especialidade">
							{specialties.map((option) => (
								<option key={option} value={option}>
									{option}
								</option>
							))}
						</chakra.select>

						<Input
							type="number"
							min={1}
							max={30}
							value={radiusKm}
							onChange={(event) => {
								const nextValue = Number.parseInt(
									event.target.value,
									10,
								);
								setRadiusKm(
									Number.isNaN(nextValue) ? 10 : nextValue,
								);
							}}
							h="46px"
							bg="surface.panel"
							borderColor="border.default"
							color="text.primary"
						/>

						<Button
							h="46px"
							bg="brand.solid"
							color="text.inverse"
							onClick={() => {
								void loadInstructors();
							}}
							loading={loading}
							_hover={{ bg: "brand.emphasized" }}>
							<Search size={16} />
							Buscar
						</Button>
					</SimpleGrid>

					<Grid
						templateColumns={{ base: "1fr", lg: "1.05fr 0.95fr" }}
						gap={4}>
						<Stack gap={3.5}>
							{loading
								? [
										"skeleton-card-1",
										"skeleton-card-2",
										"skeleton-card-3",
									].map((key) => (
										<Skeleton
											key={key}
											h="180px"
											borderRadius="2xl"
										/>
									))
								: null}

							{!loading && instructors.length === 0 ? (
								<Box
									py={16}
									px={6}
									textAlign="center"
									bg="surface.panel"
									border="1px dashed"
									borderColor="border.default"
									borderRadius="2xl">
									<Text
										fontWeight="700"
										color="text.secondary">
										Nenhum instrutor encontrado com este
										filtro.
									</Text>
									<Text
										mt={1.5}
										color="text.muted"
										fontSize="sm">
										Tente aumentar o raio de busca ou
										remover filtros.
									</Text>
								</Box>
							) : null}

							{loading
								? null
								: instructors.map((instructor) => (
										<InstructorCard
											key={instructor.id}
											instructor={instructor}
											selected={
												instructor.id ===
												selectedInstructor?.id
											}
											onOpenProfile={() =>
												onOpenProfile()
											}
											onBook={onStartBooking}
										/>
									))}
						</Stack>

						<InstructorMap
							instructors={instructors}
							selectedInstructorId={selectedInstructor?.id}
							onSelect={setSelectedInstructorId}
							onBook={onStartBooking}
						/>
					</Grid>
				</Stack>
			</Container>
		</Stack>
	);
}
