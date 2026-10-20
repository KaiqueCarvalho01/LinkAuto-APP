import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Compass,
  ChevronRight,
  CalendarClock,
  LogOut,
  Shield,
  User as UserIcon,
  Save,
  CheckCircle,
  AlertTriangle,
  ExternalLink,
  type LucideIcon,
} from "lucide-react";
import {
  Box,
  Button,
  HStack,
  Stack,
  Text,
  Input,
  Textarea,
  NativeSelect,
  Heading,
  SimpleGrid,
  Badge,
  Field,
} from "@chakra-ui/react";

import { apiErrorMessage } from "../services/apiErrorMessage";
import { profileService } from "../services/profileService";
import type { SessionData, UserAccount } from "../types/session";

interface ProfileProps {
  readonly session: SessionData | null;
  readonly token: string | undefined;
  readonly onLogout: () => void;
  readonly onProfileUpdated: (updatedUser: UserAccount) => void;
  readonly onNavigateToSearch: () => void;
  readonly onNavigateToBookings: () => void;
}

interface MenuItem {
  readonly id: string;
  readonly icon: LucideIcon;
  readonly label: string;
  readonly iconColor: string;
  readonly action: () => void;
}

type ProfileSide = "instructor" | "student";

interface ProfileFormValues {
  fullName: string;
  phone: string;
  city: string;
  state: string;
  licenseType: string;
  bio: string;
  pricePerHour: string;
  actionRadiusKm: string;
  specialtiesText: string;
}

// The stored values of one of the user's profiles, as form strings
const formValuesFor = (user: UserAccount | undefined, side: ProfileSide): ProfileFormValues => {
  const profile = side === "instructor" ? user?.instructor_profile : user?.student_profile;
  const instructor = user?.instructor_profile;
  return {
    fullName: profile?.full_name ?? "",
    phone: profile?.phone ?? "",
    city: profile?.city ?? "",
    state: profile?.state ?? "",
    licenseType: (user?.student_profile?.license_type as string | undefined) ?? "NENHUMA",
    bio: instructor?.bio ?? "",
    pricePerHour: instructor?.price_per_hour?.toString() ?? "",
    actionRadiusKm: instructor?.action_radius_km?.toString() ?? "",
    specialtiesText: instructor?.specialties?.join(", ") ?? "",
  };
};

const formatPrice = (value: string): string => {
  const price = parseFloat(value);
  return Number.isFinite(price)
    ? price.toLocaleString("pt-BR", { style: "currency", currency: "BRL" })
    : "Não informado";
};

export default function Profile({
  session,
  token,
  onLogout,
  onProfileUpdated,
  onNavigateToSearch,
  onNavigateToBookings,
}: ProfileProps) {
  const user = session?.user;
  const isInstructor = user?.roles.includes("INSTRUTOR") ?? false;
  // Public profiles are addressed by slug; internal IDs are rejected by the API
  const publicSlug = isInstructor
    ? user?.instructor_profile?.slug
    : user?.student_profile?.slug;
  const publicProfilePath = publicSlug
    ? `${isInstructor ? "/instructors" : "/students"}/${publicSlug}`
    : null;
  const isStudent = user?.roles.includes("ALUNO") ?? false;
  const isAdmin = user?.roles.includes("ADMIN") ?? false;
  const navigate = useNavigate();

  // Which profile the card shows and edits; users with both roles can switch
  const [side, setSide] = useState<ProfileSide>(isInstructor ? "instructor" : "student");
  const editsInstructor = side === "instructor";
  const hasBothProfiles = isInstructor && isStudent;
  // What is stored: the read-only view always shows this, never unsaved form values
  const saved = formValuesFor(user, side);

  // Form State, (re)seeded from the stored profile whenever editing starts
  const [isEditing, setIsEditing] = useState(false);
  const [fullName, setFullName] = useState<string>(saved.fullName);
  const [phone, setPhone] = useState<string>(saved.phone);
  const [city, setCity] = useState<string>(saved.city);
  const [state, setState] = useState<string>(saved.state);
  // Student specific form state
  const [licenseType, setLicenseType] = useState<string>(saved.licenseType);
  // Instructor specific form state
  const [bio, setBio] = useState<string>(saved.bio);
  const [pricePerHour, setPricePerHour] = useState<string>(saved.pricePerHour);
  const [actionRadiusKm, setActionRadiusKm] = useState<string>(saved.actionRadiusKm);
  const [specialtiesText, setSpecialtiesText] = useState<string>(saved.specialtiesText);

  const seedForm = (nextSide: ProfileSide) => {
    const values = formValuesFor(user, nextSide);
    setFullName(values.fullName);
    setPhone(values.phone);
    setCity(values.city);
    setState(values.state);
    setLicenseType(values.licenseType);
    setBio(values.bio);
    setPricePerHour(values.pricePerHour);
    setActionRadiusKm(values.actionRadiusKm);
    setSpecialtiesText(values.specialtiesText);
  };

  const startEditing = () => {
    seedForm(side);
    setSuccessMsg(null);
    setErrorMsg(null);
    setIsEditing(true);
  };

  const switchSide = (nextSide: ProfileSide) => {
    setSide(nextSide);
    if (isEditing) seedForm(nextSide);
  };

  const [saving, setSaving] = useState(false);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const calculateCompleteness = () => {
    const common = [saved.fullName, saved.phone, saved.city, saved.state].map((v) => v.trim());
    const fields = editsInstructor
      ? [
          ...common,
          saved.bio.trim(),
          saved.specialtiesText.trim(),
          parseFloat(saved.pricePerHour) > 0 ? "yes" : "",
          parseInt(saved.actionRadiusKm, 10) > 0 ? "yes" : "",
        ]
      : [...common, saved.licenseType !== "NENHUMA" ? "yes" : ""];
    return Math.round((fields.filter(Boolean).length / fields.length) * 100);
  };

  const completeness = calculateCompleteness();

  const handleSaveProfile = async () => {
    if (!token) return;
    setSaving(true);
    setSuccessMsg(null);
    setErrorMsg(null);

    try {
      let updatedUser: UserAccount;
      if (editsInstructor) {
        updatedUser = await profileService.updateInstructorProfile(
          {
            fullName: fullName.trim() !== "" ? fullName : undefined,
            phone: phone.trim() !== "" ? phone : undefined,
            city: city.trim() !== "" ? city : undefined,
            state: state.trim() !== "" ? state : undefined,
            bio: bio.trim() !== "" ? bio : undefined,
            pricePerHour: pricePerHour.trim() !== "" ? parseFloat(pricePerHour) : undefined,
            actionRadiusKm: actionRadiusKm.trim() !== "" ? parseInt(actionRadiusKm, 10) : undefined,
            specialties: specialtiesText.split(",").map((s) => s.trim()).filter(Boolean),
          },
          token
        );
      } else {
        updatedUser = await profileService.updateStudentProfile(
          {
            fullName: fullName.trim() !== "" ? fullName : undefined,
            phone: phone.trim() !== "" ? phone : undefined,
            city: city.trim() !== "" ? city : undefined,
            state: state.trim() !== "" ? state : undefined,
            licenseType: licenseType,
          },
          token
        );
      }

      onProfileUpdated(updatedUser);
      setSuccessMsg("Perfil atualizado com sucesso!");
      setIsEditing(false);
    } catch (err: unknown) {
      console.error("Error saving profile:", err);
      setErrorMsg(
        apiErrorMessage(err, "Erro ao salvar perfil. Tente novamente.", {
          VALIDATION_ERROR:
            "Algum campo do perfil tem um valor fora do permitido. Confira e tente novamente.",
        })
      );
    } finally {
      setSaving(false);
    }
  };

  const roleLabel = isAdmin ? "Administrador" : isInstructor ? "Instrutor" : "Aluno";

  const menuItems: MenuItem[] = [
    ...(isStudent
      ? [
          {
            id: "search",
            icon: Compass,
            label: "Buscar instrutores",
            iconColor: "brand.600",
            action: onNavigateToSearch,
          },
          {
            id: "bookings",
            icon: CalendarClock,
            label: "Meus agendamentos",
            iconColor: "brand.700",
            action: onNavigateToBookings,
          },
        ]
      : []),
    ...(publicProfilePath
      ? [
          {
            id: "public-profile",
            icon: ExternalLink,
            label: "Visualizar meu perfil público",
            iconColor: "brand.solid",
            action: () => navigate(publicProfilePath),
          },
        ]
      : []),
    {
      id: "security",
      icon: Shield,
      label: "Segurança e senha",
      iconColor: "laBlue.700",
      action: () => navigate("/password-reset"),
    },
  ];

  return (
    <Stack
      minH="100vh"
      px={{ base: 4, md: 8 }}
      py={{ base: 6, md: 8 }}
      gap={6}>
      <Box
        position="relative"
        overflow="hidden"
        borderRadius="3xl"
        p={{ base: 6, md: 8 }}
        bgGradient="linear(140deg, #0f2f47 0%, #1f5b86 52%, #338640 100%)"
        boxShadow="0 24px 56px rgba(19, 62, 93, 0.26)">
        <Box
          position="absolute"
          w="180px"
          h="180px"
          right="-42px"
          top="-42px"
          borderRadius="full"
          bg="whiteAlpha.200"
          filter="blur(2px)"
        />

        <HStack align="center" gap={4} position="relative" zIndex={1}>
          <Box
            w="72px"
            h="72px"
            borderRadius="2xl"
            display="grid"
            placeItems="center"
            bg="whiteAlpha.250"
            border="1px solid"
            borderColor="text-foreground">
            <UserIcon size={26} />
          </Box>
          <Stack gap={1} flex="1">
            <Text
              color="text.primary"
              fontFamily="heading"
              fontSize={{ base: "xl", md: "2xl" }}
              fontWeight="800">
              {saved.fullName || user?.email.split("@")[0] || "Usuário"}
            </Text>
            <Text color="text.muted" fontWeight="600" fontSize="sm">
              {user?.email}
            </Text>
            <HStack mt={1} gap={2} align="center" flexWrap="wrap">
              <Box
                px={3}
                py={1}
                borderRadius="full"
                bg="whiteAlpha.250"
                border="1px solid"
                borderColor="border.emphasized">
                <Text
                  color="text.muted"
                  fontSize="2xs"
                  fontWeight="800"
                  letterSpacing="0.14em"
                  textTransform="uppercase">
                  Conta {roleLabel}
                </Text>
              </Box>
              {publicProfilePath && (
                <Button
                  size="xs"
                  variant="outline"
                  borderColor="border.emphasized"
                  bg="whiteAlpha.250"
                  color="text.primary"
                  _hover={{ bg: "whiteAlpha.350" }}
                  onClick={() => navigate(publicProfilePath)}>
                  <ExternalLink size={12} />
                  Ver perfil público
                </Button>
              )}
            </HStack>
          </Stack>
        </HStack>

        {/* Completude do Perfil */}
        <Stack mt={6} gap={2} position="relative" zIndex={1}>
          <HStack justify="space-between">
            <Text color="text.primary" fontSize="xs" fontWeight="800">
              Completude do Perfil
            </Text>
            <Text color="text.primary" fontSize="xs" fontWeight="800">
              {completeness}%
            </Text>
          </HStack>
          <Box w="100%" h="8px" bg="whiteAlpha.200" borderRadius="full" overflow="hidden">
            <Box w={`${completeness}%`} h="100%" bg="laGreen.500" transition="width 0.5s ease" />
          </Box>
          {completeness < 100 && (
            <Text color="whiteAlpha.800" fontSize="2xs" fontWeight="600" mt={1}>
              ⚠️ Preencha todas as informações para aumentar sua relevância na plataforma.
            </Text>
          )}
        </Stack>
      </Box>

      {successMsg && (
        <HStack
          p={4}
          bg="green.50"
          color="green.700"
          borderRadius="xl"
          border="1px solid"
          borderColor="green.200"
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
          gap={2}>
          <AlertTriangle size={18} />
          <Text fontSize="sm" fontWeight="600">
            {errorMsg}
          </Text>
        </HStack>
      )}

      <Box
        bg="surface.panel"
        borderRadius="3xl"
        p={6}
        border="1px solid"
        borderColor="border.subtle">
        <Stack gap={4}>
          <HStack justify="space-between">
            <Heading fontSize="xl" color="text.primary">
              Informações do Perfil
            </Heading>
            {!isEditing ? (
              <Button size="sm" onClick={startEditing}>
                Editar Perfil
              </Button>
            ) : (
              <HStack gap={2}>
                {/* Unsaved changes are dropped: the card shows the stored profile again */}
                <Button size="sm" variant="outline" onClick={() => setIsEditing(false)}>
                  Cancelar
                </Button>
                <Button
                  size="sm"
                  bg="brand.solid"
                  color="text.inverse"
                  loading={saving}
                  onClick={handleSaveProfile}>
                  <Save size={14} />
                  Salvar
                </Button>
              </HStack>
            )}
          </HStack>

          {hasBothProfiles && (
            <HStack gap={2} role="group" aria-label="Perfil exibido">
              {(["instructor", "student"] as const).map((option) => (
                <Button
                  key={option}
                  size="xs"
                  variant={side === option ? "solid" : "outline"}
                  aria-pressed={side === option}
                  disabled={saving}
                  onClick={() => switchSide(option)}>
                  {option === "instructor" ? "Perfil de instrutor" : "Perfil de aluno"}
                </Button>
              ))}
            </HStack>
          )}

          {isEditing ? (
            <Stack gap={3} pt={2}>
              <Field.Root>
                <Field.Label fontSize="xs" fontWeight="700" color="text.secondary">
                  Nome Completo
                </Field.Label>
                <Input
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Nome Completo"
                  color="text.primary"
                />
              </Field.Root>

              <Field.Root>
                <Field.Label fontSize="xs" fontWeight="700" color="text.secondary">
                  Telefone
                </Field.Label>
                <Input
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  placeholder="Telefone"
                  color="text.primary"
                />
              </Field.Root>

              <SimpleGrid columns={2} gap={3}>
                <Field.Root>
                  <Field.Label fontSize="xs" fontWeight="700" color="text.secondary">
                    Cidade
                  </Field.Label>
                  <Input
                    value={city}
                    onChange={(e) => setCity(e.target.value)}
                    placeholder="Cidade"
                    color="text.primary"
                  />
                </Field.Root>
                <Field.Root>
                  <Field.Label fontSize="xs" fontWeight="700" color="text.secondary">
                    Estado
                  </Field.Label>
                  <Input
                    value={state}
                    onChange={(e) => setState(e.target.value)}
                    placeholder="Estado"
                    maxLength={2}
                    color="text.primary"
                  />
                </Field.Root>
              </SimpleGrid>

              {!editsInstructor ? (
                <Field.Root>
                  <Field.Label fontSize="xs" fontWeight="700" color="text.secondary">
                    Status de Habilitação
                  </Field.Label>
                  <NativeSelect.Root>
                    <NativeSelect.Field
                      value={licenseType}
                      onChange={(e) => setLicenseType(e.target.value)}
                      borderColor="border.default"
                      bg="surface.panel"
                      fontSize="sm"
                      fontWeight="600"
                      color="text.primary">
                      <option value="NENHUMA">Não habilitado (Zero)</option>
                      <option value="EM_PROCESSO">Primeira Habilitação (Autoescola)</option>
                      <option value="A">Categoria A (Moto)</option>
                      <option value="B">Categoria B (Carro)</option>
                      <option value="AB">Categoria AB (Carro e Moto)</option>
                    </NativeSelect.Field>
                    <NativeSelect.Indicator />
                  </NativeSelect.Root>
                </Field.Root>
              ) : (
                <Stack gap={3}>
                  <Field.Root>
                    <Field.Label fontSize="xs" fontWeight="700" color="text.secondary">
                      Preço da Hora (R$)
                    </Field.Label>
                    <Input
                      type="number"
                      min={0}
                      max={99999.99}
                      step="0.01"
                      value={pricePerHour}
                      onChange={(e) => setPricePerHour(e.target.value)}
                      placeholder="Valor por Hora"
                      color="text.primary"
                    />
                  </Field.Root>
                  <Field.Root>
                    <Field.Label fontSize="xs" fontWeight="700" color="text.secondary">
                      Raio de Atuação (KM)
                    </Field.Label>
                    <Input
                      type="number"
                      min={1}
                      max={200}
                      value={actionRadiusKm}
                      onChange={(e) => setActionRadiusKm(e.target.value)}
                      placeholder="Raio de atuação em km"
                      color="text.primary"
                    />
                  </Field.Root>
                  <Field.Root>
                    <Field.Label fontSize="xs" fontWeight="700" color="text.secondary">
                      Especialidades (separadas por vírgula)
                    </Field.Label>
                    <Input
                      value={specialtiesText}
                      onChange={(e) => setSpecialtiesText(e.target.value)}
                      placeholder="Ex: Baliza, Rodovias, Reciclagem"
                      color="text.primary"
                    />
                    <HStack flexWrap="wrap" gap={1} mt={2}>
                      {specialtiesText.split(",").map((s) => s.trim()).filter(Boolean).map((spec) => (
                        <Badge key={spec} colorPalette="brand" variant="subtle" rounded="md" px={2} py={0.5} fontSize="2xs">
                          {spec}
                        </Badge>
                      ))}
                    </HStack>
                  </Field.Root>
                  <Field.Root>
                    <Field.Label fontSize="xs" fontWeight="700" color="text.secondary">
                      Biografia Profissional
                    </Field.Label>
                    <Textarea
                      value={bio}
                      onChange={(e) => setBio(e.target.value)}
                      placeholder="Fale um pouco sobre sua didática e especialidades..."
                      color="text.primary"
                      rows={3}
                    />
                  </Field.Root>
                </Stack>
              )}
            </Stack>
          ) : (
            <Stack gap={2.5} pt={2} fontSize="sm" color="text.secondary" fontWeight="600">
              <HStack justify="space-between" borderBottom="1px solid" borderColor="border.subtle" pb={1.5}>
                <Text color="text.muted">Nome</Text>
                <Text color="text.primary">{saved.fullName || "Não informado"}</Text>
              </HStack>
              <HStack justify="space-between" borderBottom="1px solid" borderColor="border.subtle" pb={1.5}>
                <Text color="text.muted">Telefone</Text>
                <Text color="text.primary">{saved.phone || "Não informado"}</Text>
              </HStack>
              <HStack justify="space-between" borderBottom="1px solid" borderColor="border.subtle" pb={1.5}>
                <Text color="text.muted">Localização</Text>
                <Text color="text.primary">
                  {saved.city && saved.state ? `${saved.city} - ${saved.state}` : "Não informado"}
                </Text>
              </HStack>
              {!editsInstructor ? (
                <HStack justify="space-between" borderBottom="1px solid" borderColor="border.subtle" pb={1.5}>
                  <Text color="text.muted">Habilitação</Text>
                  <Text color="text.primary">{saved.licenseType}</Text>
                </HStack>
              ) : (
                <>
                  <HStack justify="space-between" borderBottom="1px solid" borderColor="border.subtle" pb={1.5}>
                    <Text color="text.muted">Valor por Hora</Text>
                    <Text color="text.primary">{formatPrice(saved.pricePerHour)}</Text>
                  </HStack>
                  <HStack justify="space-between" borderBottom="1px solid" borderColor="border.subtle" pb={1.5}>
                    <Text color="text.muted">Raio de Atuação</Text>
                    <Text color="text.primary">{saved.actionRadiusKm ? `${saved.actionRadiusKm} km` : "Não informado"}</Text>
                  </HStack>
                  <Box borderBottom="1px solid" borderColor="border.subtle" pb={1.5}>
                    <Text color="text.muted" mb={1.5}>Especialidades</Text>
                    <HStack flexWrap="wrap" gap={1.5}>
                      {user?.instructor_profile?.specialties && user.instructor_profile.specialties.length > 0 ? (
                        user.instructor_profile.specialties.map((spec) => (
                          <Badge key={spec} colorPalette="brand" variant="subtle" rounded="md" px={2} py={0.5}>
                            {spec}
                          </Badge>
                        ))
                      ) : (
                        <Text fontSize="xs" color="text.muted" fontWeight="500">Nenhuma especialidade cadastrada.</Text>
                      )}
                    </HStack>
                  </Box>
                  <Box pt={1}>
                    <Text color="text.muted" mb={1}>Biografia</Text>
                    <Text
                      p={3}
                      bg="surface.muted"
                      borderRadius="xl"
                      fontSize="xs"
                      color="text.primary"
                      fontWeight="500">
                      {saved.bio || "Nenhuma biografia informada."}
                    </Text>
                  </Box>
                </>
              )}
            </Stack>
          )}
        </Stack>
      </Box>

      <Box
        bg="surface.panel"
        borderRadius="3xl"
        p={3}
        border="1px solid"
        borderColor="border.subtle">
        <Stack gap={1}>
          {menuItems.map((item) => {
            const ItemIcon = item.icon;
            return (
              <Button
                key={item.id}
                onClick={item.action}
                justifyContent="space-between"
                variant="ghost"
                h="58px"
                borderRadius="2xl"
                px={3.5}
                _hover={{ bg: "surface.muted" }}>
                <HStack align="center" gap={3}>
                  <Box
                    w="36px"
                    h="36px"
                    display="grid"
                    placeItems="center"
                    bg="surface.muted"
                    borderRadius="xl"
                    color={item.iconColor}>
                    <ItemIcon size={18} />
                  </Box>
                  <Text color="text.primary" fontWeight="700">
                    {item.label}
                  </Text>
                </HStack>
                <ChevronRight
                  size={16}
                  color="var(--chakra-colors-text-muted)"
                />
              </Button>
            );
          })}
        </Stack>
      </Box>

      <Button
        onClick={onLogout}
        h="56px"
        borderRadius="2xl"
        bg="state.danger.bg"
        color="state.danger.fg"
        border="1px solid"
        borderColor="state.danger.border"
        fontWeight="800"
        gap={2}
        _hover={{ filter: "brightness(0.95)" }}>
        <LogOut size={18} />
        Sair da conta
      </Button>

      <Text
        textAlign="center"
        color="text.muted"
        fontSize="xs"
        fontWeight="600"
        letterSpacing="0.08em">
        Fatec Mogi Mirim • ADS • 2026
      </Text>
    </Stack>
  );
}
