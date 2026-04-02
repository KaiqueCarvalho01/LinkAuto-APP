import React, { useState } from "react";
import { ChevronLeft, Star, ShieldCheck, Clock, Check } from "lucide-react";

const InstructorProfile = ({ instructor, onBack, onConfirm }) => {
  const [selectedSlots, setSelectedSlots] = useState([]);
  const timeSlots = ["08:00", "09:00", "10:00", "11:00", "14:00", "15:00", "16:00"];

  const handleSlotClick = (slot) => {
    if (selectedSlots.includes(slot)) {
      setSelectedSlots(selectedSlots.filter(s => s !== slot));
    } else {
      setSelectedSlots([...selectedSlots, slot].sort());
    }
  };

  return (
    <div className="flex flex-col min-h-screen bg-[#F8F9FC] font-sans pb-10">
      {/* Cabeçalho Ajustado - Menos altura */}
      <div className="bg-gradient-to-b from-[#2563EB] to-[#3B82F6] pt-8 pb-16 px-6 rounded-b-[32px] relative">
        <button onClick={onBack} className="p-2 bg-white/20 backdrop-blur-md rounded-full text-white mb-2">
          <ChevronLeft size={20} />
        </button>
        
        <div className="flex flex-col items-center">
          <div className="relative mb-3">
            <img 
              src={instructor.photo} 
              className="w-24 h-24 rounded-[28px] border-4 border-white shadow-lg object-cover" 
              alt={instructor.name} 
            />
            <div className="absolute -bottom-1 -right-1 bg-green-500 text-white p-1 rounded-lg border-2 border-white shadow-md">
              <ShieldCheck size={16} />
            </div>
          </div>
          <h2 className="text-white text-xl font-bold">{instructor.name}</h2>
          <div className="flex items-center gap-2 mt-0.5">
            <span className="text-blue-100 text-[10px] font-black uppercase tracking-widest">{instructor.neighborhood}</span>
            <span className="text-blue-300">•</span>
            <div className="flex items-center gap-1 text-yellow-400 font-bold text-xs">
              <Star size={12} className="fill-current" /> {instructor.rating}
            </div>
          </div>
        </div>
      </div>

      {/* Card de Preço Ajustado - Agora com margem lateral correta */}
      <div className="px-5 -mt-8">
        <div className="bg-white rounded-[24px] p-5 shadow-xl shadow-blue-900/5 flex justify-between items-center mb-6">
          <div className="flex flex-col">
            <p className="text-[9px] text-gray-400 font-black uppercase tracking-widest mb-0.5">Preço por aula</p>
            <p className="text-xl font-black text-gray-800 tracking-tight">R$ {instructor.price},00</p>
          </div>
          <div className="flex flex-col items-end">
            <p className="text-[9px] text-gray-400 font-black uppercase tracking-widest mb-1">Status</p>
            <span className="bg-green-50 text-green-600 text-[9px] font-black px-2.5 py-1 rounded-lg border border-green-100">
              VALIDADO
            </span>
          </div>
        </div>

        {/* Seção de Horários */}
        <section className="mb-6 px-1">
          <h3 className="font-bold text-gray-800 text-base mb-4">Escolha os horários</h3>
          <div className="grid grid-cols-3 gap-3">
            {timeSlots.map((slot) => (
              <button
                key={slot}
                onClick={() => handleSlotClick(slot)}
                className={`py-3.5 rounded-2xl font-bold text-xs transition-all border ${
                  selectedSlots.includes(slot)
                    ? "bg-blue-600 border-blue-600 text-white shadow-md"
                    : "bg-white border-gray-100 text-gray-500 shadow-sm"
                }`}
              >
                {slot}
              </button>
            ))}
          </div>
        </section>

        {/* Botão de Confirmação */}
        <div className="px-1 space-y-4">
          <button
            disabled={selectedSlots.length === 0}
            onClick={() => onConfirm(instructor, selectedSlots)}
            className={`w-full py-4 rounded-[20px] font-bold text-base shadow-lg transition-all flex items-center justify-center gap-2 ${
              selectedSlots.length > 0
                ? "bg-[#0F172A] text-white active:scale-95" 
                : "bg-gray-200 text-gray-400 cursor-not-allowed"
            }`}
          >
            Confirmar Agendamento {selectedSlots.length > 0 && <Check size={18} />}
          </button>
        </div>
      </div>
    </div>
  );
};

export default InstructorProfile;