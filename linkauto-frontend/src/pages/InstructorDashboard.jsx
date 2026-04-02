import React from "react";
import { Check, X, Calendar, DollarSign, Star, Users, Clock } from "lucide-react";

const InstructorDashboard = ({ instructorData, requests, onAccept, onReject }) => {
  return (
    <div className="flex flex-col min-h-screen bg-[#F8F9FC] font-sans pb-20">
      <div className="bg-gradient-to-b from-[#0F172A] to-[#1E293B] pt-10 pb-20 px-6 rounded-b-[40px] relative text-white">
        <div className="flex justify-between items-center mb-6">
          <div>
            <p className="text-blue-400 text-[10px] font-black uppercase tracking-widest">Painel do Instrutor</p>
            <h2 className="text-2xl font-bold">{instructorData.name}</h2>
          </div>
          <div className="bg-white/10 backdrop-blur-md p-2 rounded-2xl border border-white/10">
            <Star className="text-yellow-400 fill-current" size={20} />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="bg-white/5 backdrop-blur-sm p-4 rounded-[24px] border border-white/10">
            <p className="text-[9px] text-gray-400 font-bold uppercase mb-1">Ganhos do Mês</p>
            <p className="text-xl font-black">R$ 1.240</p>
          </div>
          <div className="bg-white/5 backdrop-blur-sm p-4 rounded-[24px] border border-white/10">
            <p className="text-[9px] text-gray-400 font-bold uppercase mb-1">Aulas Feitas</p>
            <p className="text-xl font-black">18</p>
          </div>
        </div>
      </div>

      <div className="px-5 -mt-8 relative z-10 space-y-6">
        <section>
          <div className="flex justify-between items-center mb-4 px-1">
            <h3 className="font-bold text-gray-800 text-base italic">Solicitações</h3>
            <span className="bg-orange-100 text-orange-600 text-[9px] font-black px-2 py-1 rounded-lg">
              {requests.length} PENDENTES
            </span>
          </div>

          <div className="space-y-4">
            {requests.length > 0 ? (
              requests.map((req) => (
                <div key={req.id} className="bg-white rounded-[28px] p-5 shadow-xl shadow-blue-900/5 border border-gray-50">
                  <div className="flex items-center gap-4 mb-4">
                    <div className="w-12 h-12 bg-slate-100 rounded-2xl flex items-center justify-center text-slate-600 font-black text-lg">
                      {req.studentName[0]}
                    </div>
                    <div className="flex-grow">
                      <h4 className="font-bold text-gray-800 text-sm">{req.studentName}</h4>
                      <p className="text-[10px] text-gray-400 font-bold uppercase">{req.neighborhood}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-blue-600 font-black text-sm">R$ {req.price}</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-4 py-3 border-y border-gray-50 mb-4">
                    <div className="flex items-center gap-1.5 text-gray-500 text-[11px] font-bold">
                      <Calendar size={14} className="text-blue-500" /> {req.date}
                    </div>
                    <div className="flex items-center gap-1.5 text-gray-500 text-[11px] font-bold">
                      <Clock size={14} className="text-blue-500" /> {req.time}h
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <button 
                      onClick={() => onReject(req.id)}
                      className="flex items-center justify-center gap-2 py-3 bg-gray-50 text-gray-500 rounded-xl font-bold text-xs active:bg-red-50 active:text-red-500 transition-all"
                    >
                      <X size={16} /> Recusar
                    </button>
                    <button 
                      onClick={() => onAccept(req.id)}
                      className="flex items-center justify-center gap-2 py-3 bg-[#0F172A] text-white rounded-xl font-bold text-xs active:scale-95 transition-all shadow-lg"
                    >
                      <Check size={16} /> Aceitar
                    </button>
                  </div>
                </div>
              ))
            ) : (
              <div className="bg-white p-10 rounded-[28px] text-center border border-dashed border-gray-200">
                <p className="text-gray-400 text-xs font-medium">Nenhuma solicitação no momento.</p>
              </div>
            )}
          </div>
        </section>

        <section className="grid grid-cols-2 gap-4 pb-10">
          <button className="bg-white p-5 rounded-[28px] border border-gray-50 shadow-sm flex flex-col items-center gap-2 active:scale-95 transition-all">
            <div className="w-10 h-10 bg-blue-50 rounded-xl flex items-center justify-center text-blue-600">
              <Users size={20} />
            </div>
            <span className="text-[10px] font-black text-gray-400 uppercase">Meus Alunos</span>
          </button>
          <button className="bg-white p-5 rounded-[28px] border border-gray-50 shadow-sm flex flex-col items-center gap-2 active:scale-95 transition-all">
            <div className="w-10 h-10 bg-green-50 rounded-xl flex items-center justify-center text-green-600">
              <DollarSign size={20} />
            </div>
            <span className="text-[10px] font-black text-gray-400 uppercase">Extrato</span>
          </button>
        </section>
      </div>
    </div>
  );
};

export default InstructorDashboard;