export interface Testimonial {
	id: number;
	name: string;
	role: string;
	text: string;
	rating: number;
	avatar?: string;
}

export const studentTestimonials: Testimonial[] = [
	{
		id: 1,
		name: "Maria Silva",
		role: "Aluna de Primeira Habilitação",
		text: "Encontrei um instrutor excelente perto de casa. A plataforma facilitou muito o agendamento!",
		rating: 5,
	},
	{
		id: 2,
		name: "Pedro Costa",
		role: "Habilitado (Medo de Dirigir)",
		text: "Perdi o medo de dirigir em poucas semanas. O feedback detalhado me deu muita confiança.",
		rating: 4.8,
	},
	{
		id: 3,
		name: "Ana Oliveira",
		role: "Aluna de Primeira Habilitação",
		text: "Sistema de pagamento seguro e suporte muito rápido. Recomendo para todos!",
		rating: 5,
	},
];

export const instructorTestimonials: Testimonial[] = [
	{
		id: 1,
		name: "Ricardo Santos",
		role: "Instrutor Credenciado",
		text: "A LinkAuto triplicou meus agendamentos. A gestão da agenda pelo celular é incrível.",
		rating: 5,
	},
	{
		id: 2,
		name: "Carla Ferreira",
		role: "Instrutora de Habilitados",
		text: "Plataforma moderna que valoriza o bom profissional. O repasse dos pagamentos é pontual.",
		rating: 4.9,
	},
	{
		id: 3,
		name: "Marcos Lima",
		role: "Instrutor Credenciado",
		text: "Fácil de usar e traz leads qualificados. O suporte ao instrutor é um diferencial.",
		rating: 5,
	},
];
