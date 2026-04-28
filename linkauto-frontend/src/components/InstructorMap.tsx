import { Button, HStack, Stack, Text } from "@chakra-ui/react";
import L, { type DivIcon } from "leaflet";
import { Circle, MapContainer, Marker, Popup, TileLayer } from "react-leaflet";

import "leaflet/dist/leaflet.css";

import { RatingStars } from "./RatingStars";
import type { InstructorSummary } from "../types/instructor";

interface InstructorMapProps {
	readonly instructors: InstructorSummary[];
	readonly selectedInstructorId: string | undefined;
	readonly onSelect: (instructorId: string) => void;
	readonly onBook: (instructor: InstructorSummary) => void;
}

const fallbackCenter: [number, number] = [-22.4331, -46.957];

const initialsFromName = (name: string): string => {
	const fragments = name
		.trim()
		.split(" ")
		.filter((fragment) => fragment.length > 0)
		.slice(0, 2);
	return fragments
		.map((fragment) => fragment[0]?.toUpperCase() ?? "")
		.join("");
};

const markerIcon = (name: string, active: boolean): DivIcon => {
	const ring = active ? "#1A6DB5" : "#D1D5DB";
	const background = active ? "#1A6DB5" : "#FFFFFF";
	const color = active ? "#FFFFFF" : "#124E87";

	return L.divIcon({
		className: "",
		html: `<div style="width:40px;height:40px;border-radius:999px;border:3px solid ${ring};background:${background};color:${color};display:grid;place-items:center;font-weight:700;font-size:12px;box-shadow:0 8px 16px rgba(17,24,39,.2)">${initialsFromName(name)}</div>`,
		iconSize: [40, 40],
		iconAnchor: [20, 20],
		popupAnchor: [0, -18],
	});
};

export function InstructorMap({
	instructors,
	selectedInstructorId,
	onSelect,
	onBook,
}: InstructorMapProps) {
	const firstInstructor = instructors[0];
	const selectedInstructor =
		instructors.find((item) => item.id === selectedInstructorId) ??
		firstInstructor;

	const mapCenter: [number, number] = selectedInstructor
		? [
				selectedInstructor.coordinates.lat,
				selectedInstructor.coordinates.lng,
			]
		: fallbackCenter;

	return (
		<Stack
			h="100%"
			minH={{ base: "340px", lg: "560px" }}
			border="1px solid"
			borderColor="border.default"
			borderRadius="2xl"
			overflow="hidden"
			bg="surface.panel"
			zIndex={0}
			aria-label="Mapa de instrutores disponiveis">
			<MapContainer
				center={mapCenter}
				zoom={12}
				style={{ height: "100%", width: "100%" }}>
				<TileLayer
					url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
					attribution="&copy; OpenStreetMap contributors &copy; CARTO"
				/>

				{instructors.map((instructor) => {
					const active = instructor.id === selectedInstructorId;
					return (
						<Marker
							key={instructor.id}
							position={[
								instructor.coordinates.lat,
								instructor.coordinates.lng,
							]}
							icon={markerIcon(instructor.fullName, active)}
							eventHandlers={{
								click: () => {
									onSelect(instructor.id);
								},
							}}>
							<Popup>
								<Stack
									gap={2.5}
									minW="220px"
									color="laGray.900">
									<Text fontWeight="700">
										{instructor.fullName}
									</Text>
									<RatingStars
										rating={instructor.rating}
										reviewsCount={instructor.reviewsCount}
									/>
									<Text
										fontSize="sm"
										color="laGray.600"
										fontWeight="500">
										{instructor.neighborhood},{" "}
										{instructor.city}
									</Text>
									<Button
										size="sm"
										bg="brand.solid"
										color="text.inverse"
										onClick={() => onBook(instructor)}
										_hover={{ bg: "brand.emphasized" }}>
										Agendar
									</Button>
								</Stack>
							</Popup>
						</Marker>
					);
				})}

				{selectedInstructor ? (
					<Circle
						center={[
							selectedInstructor.coordinates.lat,
							selectedInstructor.coordinates.lng,
						]}
						radius={selectedInstructor.radiusKm * 1000}
						pathOptions={{
							color: "#1A6DB5",
							fillColor: "#D6E8F7",
							fillOpacity: 0.2,
							weight: 1.5,
						}}
					/>
				) : null}
			</MapContainer>

			{selectedInstructor ? (
				<HStack
					px={4}
					py={2.5}
					borderTop="1px solid"
					borderColor="border.subtle">
					<Text fontSize="sm" color="text.secondary" fontWeight="600">
						Raio de atendimento de {selectedInstructor.fullName}:{" "}
						{selectedInstructor.radiusKm} km
					</Text>
				</HStack>
			) : null}
		</Stack>
	);
}
