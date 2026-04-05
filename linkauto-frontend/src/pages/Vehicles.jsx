import React from "react";
import { Car, ChevronLeft, Plus, Trash2, ShieldCheck } from "lucide-react";

const Vehicles = ({ onBack }) => {
  const myVehicles = [
    { id: 1, model: "Chevrolet Onix", plate: "BRA2E19", color: "Branco", type: "Manual", status: "Ativo" },
    { id: 2, model: "Hyundai HB20", plate: "KJK5F22", color: "Prata", type: "Automático", status: "Em verificação" }
  ];

  return (
    <div className="flex flex-col min-h-screen bg-[#F8F9FC] font-sans pb-24">
      {/* Header Fixo */}
      <div className="bg-white px-6 pt-12 pb-6 flex items-center gap-4 border-b border-gray-100 sticky top-0 z-30">
        <button 
          onClick={onBack}
          className="p-2 hover:bg-gray-50 rounded-xl transition-colors"
        >
          <ChevronLeft size={24} className="text-gray-900" />
        </button>
        <h1 className="text-xl font-black text-gray-900 tracking-tight">Meus Veículos</h1>
      </div>

      <div className="px-5 py-6 space-y-4">
        {/* Card de Informação */}
        <div className="bg-blue-600 rounded-[32px] p-6 text-white shadow-xl shadow-blue-200 flex items-center gap-4">
          <div className="bg-white/20 p-3 rounded-2xl backdrop-blur-md">
            <ShieldCheck size={28} />
          </div>
          <div>
            <p className="text-blue-100 text-xs font-bold uppercase tracking-wider">Segurança LinkAuto</p>
            <h3 className="text-sm font-medium leading-tight">Apenas veículos verificados podem ser utilizados em aulas.</h3>
          </div>
        </div>

        {/* Lista de Veículos */}
        <div className="space-y-4 pt-2">
          {myVehicles.map((vehicle) => (
            <div key={vehicle.id} className="bg-white rounded-[28px] p-5 border border-gray-100 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden group">
              <div className="flex gap-4 items-center">
                <div className="w-16 h-16 bg-gray-50 rounded-2xl flex items-center justify-center text-blue-600">
                  <Car size={32} />
                </div>
                <div className="flex-grow">
                  <div className="flex items-center justify-between">
                    <h3 className="font-bold text-gray-900">{vehicle.model}</h3>
                    <span className={`text-[10px] font-black px-2 py-1 rounded-full uppercase ${
                      vehicle.status === 'Ativo' ? 'bg-green-100 text-green-600' : 'bg-orange-100 text-orange-600'
                    }`}>
                      {vehicle.status}
                    </span>
                  </div>
                  <div className="flex items-center gap-3 mt-1">
                    <span className="text-xs font-bold text-gray-400 bg-gray-50 px-2 py-0.5 rounded-md uppercase tracking-tighter">
                      {vehicle.plate}
                    </span>
                    <span className="text-xs text-gray-400 font-medium">•</span>
                    <span className="text-xs text-gray-400 font-medium">{vehicle.color}</span>
                    <span className="text-xs text-gray-400 font-medium">•</span>
                    <span className="text-xs text-gray-400 font-medium">{vehicle.type}</span>
                  </div>
                </div>
              </div>
              
              <div className="mt-4 pt-4 border-t border-gray-50 flex justify-end gap-3">
                <button className="p-2 text-red-400 hover:bg-red-50 rounded-xl transition-colors">
                  <Trash2 size={18} />
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Botão Adicionar */}
        <button className="w-full bg-white border-2 border-dashed border-gray-200 rounded-[28px] p-8 flex flex-col items-center justify-center gap-3 text-gray-400 hover:border-blue-300 hover:text-blue-500 transition-all group">
          <div className="p-3 bg-gray-50 rounded-full group-hover:bg-blue-50 transition-colors">
            <Plus size={24} />
          </div>
          <span className="font-bold text-sm">Adicionar novo veículo</span>
        </button>
      </div>
    </div>
  );
};

export default Vehicles;
