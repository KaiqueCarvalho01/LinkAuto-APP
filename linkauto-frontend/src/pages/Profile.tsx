import { useState } from "react";
import {
  Bell,
  Car,
  Compass,
  ChevronRight,
  CreditCard,
  CalendarClock,
  LogOut,
  Shield,
  User as UserIcon,
  Save,
  CheckCircle,
  AlertTriangle,
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
  chakra,
  Heading,
  SimpleGrid,
} from "@chakra-ui/react";

import { profileService } from "../services/profileService";
import type { SessionData, UserAccount } from "../types/session";

interface ProfileProps {
  readonly session: SessionData | null;
  readonly token: string | undefined;
  readonly onLogout: () => void;
  readonly onProfileUpdated: (updatedUser: UserAccount) => void;
  readonly onNavigateToSearch: () => void;
  readonly onNavigateToBookings: () => void;
  readonly onNavigateToVehicles: () => void;
}

interface MenuItem {
  readonly id: string;
  readonly icon: LucideIcon;
  readonly label: string;
  readonly iconColor: string;
  readonly action?: () => void;
}

export default function Profile({
  session,
  token,
  onLogout,
  onProfileUpdated,
  onNavigateToSearch,
  onNavigateToBookings,
  onNavigateToVehicles,
}: ProfileProps) {
  const user = session?.user;
  const isInstructor = user?.roles.includes("INSTRUTOR") ?? false;
  const isAdmin = user?.roles.includes("ADMIN") ?? false;

  // Form State
  const [isEditing, setIsEditing] = useState(false);
  const [fullName, setFullName] = useState<string>(
    isInstructor
      ? (user?.instructor_profile?.full_name as string ?? "")
      : (user?.student_profile?.full_name as string ?? "")
  );
  const [phone, setPhone] = useState<string>(
    isInstructor
      ? (user?.instructor_profile?.phone as string ?? "")
      : (user?.student_profile?.phone as string ?? "")
  );
  const [city, setCity] = useState<string>(
    isInstructor
      ? (user?.instructor_profile?.city as string ?? "")
      : (user?.student_profile?.city as string ?? "")
  );
  const [state, setState] = useState<string>(
    isInstructor
      ? (user?.instructor_profile?.state as string ?? "")
      : (user?.student_profile?.state as string ?? "")
  );

  // Student specific form state
  const [licenseType, setLicenseType] = useState<string>(
    user?.student_profile?.license_type as string ?? "NENHUMA"
  );

  // Instructor specific form state
  const [bio, setBio] = useState<string>(user?.instructor_profile?.bio as string ?? "");
  const [pricePerHour, setPricePerHour] = useState<string>(
    user?.instructor_profile?.price_per_hour?.toString() ?? "70"
  );
  const [actionRadiusKm, setActionRadiusKm] = useState<string>(
    user?.instructor_profile?.action_radius_km?.toString() ?? "15"
  );

  const [saving, setSaving] = useState(false);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleSaveProfile = async () => {
    if (!token) return;
    setSaving(true);
    setSuccessMsg(null);
    setErrorMsg(null);

    try {
      let updatedUser: UserAccount;
      if (isInstructor) {
        updatedUser = await profileService.updateInstructorProfile(
          {
            fullName: fullName.trim() !== "" ? fullName : undefined,
            phone: phone.trim() !== "" ? phone : undefined,
            city: city.trim() !== "" ? city : undefined,
            state: state.trim() !== "" ? state : undefined,
            bio: bio.trim() !== "" ? bio : undefined,
            pricePerHour: pricePerHour.trim() !== "" ? parseFloat(pricePerHour) : undefined,
            actionRadiusKm: actionRadiusKm.trim() !== "" ? parseInt(actionRadiusKm, 10) : undefined,
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
    } catch (err: any) {
      console.error("Error saving profile:", err);
      setErrorMsg(err.message || "Erro ao salvar perfil. Tente novamente.");
    } finally {
      setSaving(false);
    }
  };

  const roleLabel = isAdmin ? "Administrador" : isInstructor ? "Instrutor" : "Aluno";

  const menuItems: MenuItem[] = [
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
    ...(isInstructor
      ? [
          {
            id: "vehicles",
            icon: Car,
            label: "Meus Veículos",
            iconColor: "accent.600",
            action: onNavigateToVehicles,
          },
        ]
      : []),
    {
      id: "notifications",
      icon: Bell,
      label: "Notificações (Em breve)",
      iconColor: "laBlue.600",
    },
    {
      id: "security",
      icon: Shield,
      label: "Segurança e senha",
      iconColor: "laBlue.700",
    },
    {
      id: "plans",
      icon: CreditCard,
      label: "Planos e assinaturas",
      iconColor: "text.secondary",
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
            <UserIcon size={26} className="text-foreground" />
          </Box>
          <Stack gap={1}>
            <Text
              color="text.primary"
              fontFamily="heading"
              fontSize={{ base: "xl", md: "2xl" }}
              fontWeight="800">
              {fullName || user?.email.split("@")[0] || "Usuário"}
            </Text>
            <Text color="text.muted" fontWeight="600" fontSize="sm">
              {user?.email}
            </Text>
            <Box
              mt={1}
              alignSelf="start"
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
          </Stack>
        </HStack>
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
              <Button size="sm" onClick={() => setIsEditing(true)}>
                Editar Perfil
              </Button>
            ) : (
              <HStack gap={2}>
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

          {isEditing ? (
            <Stack gap={3} pt={2}>
              <Box>
                <Text fontSize="xs" fontWeight="700" mb={1} color="text.secondary">
                  Nome Completo
                </Text>
                <Input
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Nome Completo"
                  color="text.primary"
                />
              </Box>

              <Box>
                <Text fontSize="xs" fontWeight="700" mb={1} color="text.secondary">
                  Telefone
                </Text>
                <Input
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  placeholder="Telefone"
                  color="text.primary"
                />
              </Box>

              <SimpleGrid columns={2} gap={3}>
                <Box>
                  <Text fontSize="xs" fontWeight="700" mb={1} color="text.secondary">
                    Cidade
                  </Text>
                  <Input
                    value={city}
                    onChange={(e) => setCity(e.target.value)}
                    placeholder="Cidade"
                    color="text.primary"
                  />
                </Box>
                <Box>
                  <Text fontSize="xs" fontWeight="700" mb={1} color="text.secondary">
                    Estado
                  </Text>
                  <Input
                    value={state}
                    onChange={(e) => setState(e.target.value)}
                    placeholder="Estado"
                    maxLength={2}
                    color="text.primary"
                  />
                </Box>
              </SimpleGrid>

              {!isInstructor ? (
                <Box>
                  <Text fontSize="xs" fontWeight="700" mb={1} color="text.secondary">
                    Status de Habilitação
                  </Text>
                  <chakra.select
                    value={licenseType}
                    onChange={(e) => setLicenseType(e.target.value)}
                    h="40px"
                    w="100%"
                    borderRadius="md"
                    border="1px solid"
                    borderColor="border.default"
                    bg="surface.panel"
                    px={3}
                    fontSize="sm"
                    fontWeight="600"
                    color="text.primary">
                    <option value="NENHUMA">Não habilitado (Zero)</option>
                    <option value="EM_PROCESSO">Primeira Habilitação (Autoescola)</option>
                    <option value="A">Categoria A (Moto)</option>
                    <option value="B">Categoria B (Carro)</option>
                    <option value="AB">Categoria AB (Carro e Moto)</option>
                  </chakra.select>
                </Box>
              ) : (
                <Stack gap={3}>
                  <Box>
                    <Text fontSize="xs" fontWeight="700" mb={1} color="text.secondary">
                      Preço da Hora (R$)
                    </Text>
                    <Input
                      type="number"
                      value={pricePerHour}
                      onChange={(e) => setPricePerHour(e.target.value)}
                      placeholder="Valor por Hora"
                      color="text.primary"
                    />
                  </Box>
                  <Box>
                    <Text fontSize="xs" fontWeight="700" mb={1} color="text.secondary">
                      Raio de Atuação (KM)
                    </Text>
                    <Input
                      type="number"
                      value={actionRadiusKm}
                      onChange={(e) => setActionRadiusKm(e.target.value)}
                      placeholder="Raio de atuação em km"
                      color="text.primary"
                    />
                  </Box>
                  <Box>
                    <Text fontSize="xs" fontWeight="700" mb={1} color="text.secondary">
                      Biografia Profissional
                    </Text>
                    <Textarea
                      value={bio}
                      onChange={(e) => setBio(e.target.value)}
                      placeholder="Fale um pouco sobre sua didática e especialidades..."
                      color="text.primary"
                      rows={3}
                    />
                  </Box>
                </Stack>
              )}
            </Stack>
          ) : (
            <Stack gap={2.5} pt={2} fontSize="sm" color="text.secondary" fontWeight="600">
              <HStack justify="space-between" borderBottom="1px solid" borderColor="border.subtle" pb={1.5}>
                <Text color="text.muted">Nome</Text>
                <Text color="text.primary">{fullName || "Não informado"}</Text>
              </HStack>
              <HStack justify="space-between" borderBottom="1px solid" borderColor="border.subtle" pb={1.5}>
                <Text color="text.muted">Telefone</Text>
                <Text color="text.primary">{phone || "Não informado"}</Text>
              </HStack>
              <HStack justify="space-between" borderBottom="1px solid" borderColor="border.subtle" pb={1.5}>
                <Text color="text.muted">Localização</Text>
                <Text color="text.primary">
                  {city && state ? `${city} - ${state}` : "Não informado"}
                </Text>
              </HStack>
              {!isInstructor ? (
                <HStack justify="space-between" borderBottom="1px solid" borderColor="border.subtle" pb={1.5}>
                  <Text color="text.muted">Habilitação</Text>
                  <Text color="text.primary">{licenseType || "NENHUMA"}</Text>
                </HStack>
              ) : (
                <>
                  <HStack justify="space-between" borderBottom="1px solid" borderColor="border.subtle" pb={1.5}>
                    <Text color="text.muted">Valor por Hora</Text>
                    <Text color="text.primary">R$ {pricePerHour},00</Text>
                  </HStack>
                  <HStack justify="space-between" borderBottom="1px solid" borderColor="border.subtle" pb={1.5}>
                    <Text color="text.muted">Raio de Atuação</Text>
                    <Text color="text.primary">{actionRadiusKm} km</Text>
                  </HStack>
                  <Box pt={1}>
                    <Text color="text.muted" mb={1}>Biografia</Text>
                    <Text
                      p={3}
                      bg="surface.muted"
                      borderRadius="xl"
                      fontSize="xs"
                      color="text.primary"
                      fontWeight="500">
                      {bio || "Nenhuma biografia informada."}
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
