import React from "react";
import {
	User,
	Mail,
	Shield,
	LogOut,
	ChevronRight,
	Bell,
	CreditCard,
	Car,
} from "lucide-react";

const Profile = ({ userData, onLogout, onNavigateToVehicles }) => {
	const resolvedUser = userData ?? {
		name: "Conta LinkAuto",
		email: "usuario@linkauto.app",
		role: "student",
	};
	const roleLabel =
		resolvedUser.role === "admin"
			? "Administrador"
			: resolvedUser.role === "instructor"
				? "Instrutor"
				: "Aluno";

	const menuItems = [
		...(resolvedUser.role === "instructor"
			? [
					{
						icon: <Car size={20} />,
						label: "Meus Veículos",
						color: "text-blue-500",
						action: onNavigateToVehicles,
					},
				]
			: []),
		{
			icon: <Bell size={20} />,
			label: "Notificações",
			color: "text-orange-500",
		},
		{
			icon: <Shield size={20} />,
			label: "Segurança e Senha",
			color: "text-green-500",
		},
		{
			icon: <CreditCard size={20} />,
			label: "Planos e Assinaturas",
			color: "text-purple-500",
		},
	];

	return (
		<div className="flex flex-col min-h-screen bg-[#F8F9FC] font-sans pb-24">
			{/* Header com Foto */}
			<div className="bg-gradient-to-b from-[#2563EB] to-[#3B82F6] pt-12 pb-20 px-6 rounded-b-[40px] relative text-center">
				<div className="relative inline-block mb-4">
					<div className="w-24 h-24 rounded-[32px] border-4 border-white shadow-xl bg-gray-100 flex items-center justify-center overflow-hidden">
						<User size={48} className="text-gray-300" />
					</div>
				</div>
				<h2 className="text-white text-xl font-bold">
					{resolvedUser.name}
				</h2>
				<p className="text-blue-100 text-xs font-medium opacity-80">
					{resolvedUser.email}
				</p>
				<span className="inline-block mt-3 bg-white/20 backdrop-blur-md text-white text-[10px] font-black px-3 py-1 rounded-full uppercase tracking-widest">
					Conta {roleLabel}
				</span>
			</div>

			{/* Opções de Menu */}
			<div className="px-5 -mt-8 relative z-10 space-y-3">
				<div className="bg-white rounded-[32px] p-2 shadow-xl shadow-blue-900/5 border border-gray-50">
					{menuItems.map((item, index) => (
						<button
							key={index}
							onClick={item.action}
							className="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-all rounded-2xl group">
							<div className="flex items-center gap-4">
								<div
									className={`p-2 rounded-xl bg-gray-50 ${item.color} group-hover:scale-110 transition-transform`}>
									{item.icon}
								</div>
								<span className="font-bold text-gray-700 text-sm">
									{item.label}
								</span>
							</div>
							<ChevronRight size={18} className="text-gray-300" />
						</button>
					))}
				</div>

				{/* Botão Logout */}
				<button
					onClick={onLogout}
					className="w-full bg-white rounded-[24px] p-5 shadow-sm border border-red-50 flex items-center justify-center gap-3 text-red-500 font-black text-sm active:scale-95 transition-all mt-6">
					<LogOut size={20} />
					SAIR DA CONTA
				</button>

				<p className="text-center text-[10px] text-gray-300 font-medium pt-4">
					LinkAuto v1.0.4 - TCC 2026
				</p>
			</div>
		</div>
	);
};

export default Profile;
