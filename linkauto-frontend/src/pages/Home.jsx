import React, { useState } from "react";
import {
  Search,
  Calendar,
  Zap,
  BarChart3,
  Car,
  Bell,
  Star,
  MapPin,
  ChevronLeft,
  ShieldCheck,
  User
} from "lucide-react";

const Home = ({ onStartSearch }) => {
  const [showVehicles, setShowVehicles] = useState(false);

  const instructorVehicles = [
    { id: 1, instructor: "Marcos Silva", model: "HB20 Manual", plate: "BRA2E19", color: "Branco", rating: 4.9, photo: "https://i.pravatar.cc/150?u=marcos" },
    { id: 2, instructor: "Ana Paula", model: "Chevrolet Onix", plate: "KJK5F22", color: "Prata", rating: 4.8, photo: "https://i.pravatar.cc/150?u=ana" },
    { id: 3, instructor: "Ricardo Silva", model: "Fiat Argo", plate: "LPV8G31", color: "Preto", rating: 4.7, photo: "https://i.pravatar.cc/150?u=ricardo" }
  ];

  const lastInstructor = {
    name: "Marcos Silva",
    distance: "5 min de você",
    car: "HB20 Manual",
    rating: 4.9,
    photo: "https://i.pravatar.cc/150?u=marcos",
  };

  if (showVehicles) {
    return (
      <div className="flex flex-col min-h-screen bg-[#F8F9FC] pb-24">
        {/* Header Veículos */}
        <div className="bg-white px-6 pt-12 pb-6 flex items-center gap-4 border-b border-gray-100 sticky top-0 z-30">
          <button 
            onClick={() => setShowVehicles(false)}
            className="p-2 hover:bg-gray-50 rounded-xl transition-colors"
          >
            <ChevronLeft size={24} className="text-gray-900" />
          </button>
          <h1 className="text-xl font-black text-gray-900 tracking-tight">Veículos das Aulas</h1>
        </div>

        <div className="px-5 py-6 space-y-4">
          <div className="bg-indigo-600 rounded-[32px] p-6 text-white shadow-xl shadow-indigo-200 flex items-center gap-4">
            <div className="bg-white/20 p-3 rounded-2xl backdrop-blur-md">
              <ShieldCheck size={28} />
            </div>
            <div>
              <p className="text-indigo-100 text-xs font-bold uppercase tracking-wider">Identificação</p>
              <h3 className="text-sm font-medium leading-tight">Confira o veículo antes de iniciar sua aula com o instrutor.</h3>
            </div>
          </div>

          <div className="space-y-4">
            {instructorVehicles.map((v) => (
              <div key={v.id} className="bg-white rounded-[28px] p-5 border border-gray-100 shadow-sm relative group overflow-hidden">
                <div className="flex justify-between items-start mb-4">
                  <div className="flex items-center gap-3">
                    <img src={v.photo} className="w-10 h-10 rounded-xl object-cover" alt="" />
                    <div>
                      <h4 className="font-bold text-gray-900 text-sm">{v.instructor}</h4>
                      <div className="flex items-center gap-1 text-yellow-500 font-bold text-[10px]">
                        <Star size={10} className="fill-current" /> {v.rating}
                      </div>
                    </div>
                  </div>
                  <div className="bg-gray-50 px-3 py-1.5 rounded-xl border border-gray-100">
                    <span className="text-[10px] font-black text-gray-400 tracking-tighter uppercase">{v.plate}</span>
                  </div>
                </div>

                <div className="flex gap-4 items-center">
                  <div className="w-16 h-16 bg-indigo-50 rounded-2xl flex items-center justify-center text-indigo-600">
                    <Car size={32} />
                  </div>
                  <div>
                    <h3 className="font-black text-gray-800 text-lg tracking-tight">{v.model}</h3>
                    <div className="flex items-center gap-2 mt-0.5">
                      <span className="text-xs text-gray-400 font-bold">{v.color}</span>
                      <span className="text-xs text-gray-300">•</span>
                      <span className="text-xs text-gray-400 font-bold uppercase tracking-widest text-[10px]">Verificado</span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col min-h-screen bg-[#F8F9FC] pb-24">
      <div className="relative h-64 bg-slate-200 overflow-hidden">
        <div
          className="absolute inset-0 opacity-20"
          style={{
            backgroundImage: "radial-gradient(#94a3b8 1px, transparent 1px)",
            backgroundSize: "30px 30px",
          }}
        ></div>
        <div className="absolute top-6 left-6 right-6 flex justify-between items-center">
          <div className="flex items-center gap-3 bg-white/90 backdrop-blur-md p-2 pr-6 rounded-full shadow-sm">
            <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center font-bold text-blue-600">
              J
            </div>
            <span className="font-bold text-gray-800">João</span>
          </div>
          <button className="p-3 bg-white rounded-full shadow-sm text-gray-400">
            <Bell size={24} />
          </button>
        </div>
        <Car
          className="absolute top-32 left-20 text-blue-500 fill-current"
          size={24}
        />
        <Car
          className="absolute top-40 right-32 text-red-500 fill-current"
          size={20}
        />
      </div>

      <div className="px-6 -mt-12 relative z-10">
        <div className="bg-white rounded-[32px] p-6 shadow-xl shadow-blue-900/5 mb-6">
          <div className="space-y-4">
            <div className="flex items-center gap-3 mb-2">
              <div className="bg-purple-100 p-2 rounded-lg text-purple-600">
                <Search size={20} />
              </div>
              <h3 className="font-bold text-gray-800 text-lg">
                O que vamos fazer hoje?
              </h3>
            </div>
            <div onClick={onStartSearch} className="relative cursor-pointer">
              <MapPin
                className="absolute left-4 top-4 text-blue-500"
                size={20}
              />
              <div className="w-full border border-gray-100 pl-12 pr-4 py-4 rounded-2xl bg-gray-50 text-gray-300">
                Digite seu bairro para buscar...
              </div>
            </div>
          </div>
          <div className="grid grid-cols-4 gap-4 mt-6 pt-6 border-t border-gray-50">
            <button
              onClick={onStartSearch}
              className="flex flex-col items-center gap-2"
            >
              <div className="w-14 h-14 bg-gray-50 rounded-2xl flex items-center justify-center text-blue-500 shadow-sm">
                <Calendar size={24} />
              </div>
              <span className="text-[10px] font-bold text-gray-400 uppercase tracking-tight">
                Agendar
              </span>
            </button>
            <button
              className="flex flex-col items-center gap-2 opacity-50 cursor-not-allowed"
            >
              <div className="w-14 h-14 bg-gray-50 rounded-2xl flex items-center justify-center shadow-sm">
                <Zap size={24} className="text-orange-500" />
              </div>
              <span className="text-[10px] font-bold text-gray-400 uppercase tracking-tight">
                Agora
              </span>
            </button>
            <button
              className="flex flex-col items-center gap-2 opacity-50 cursor-not-allowed"
            >
              <div className="w-14 h-14 bg-gray-50 rounded-2xl flex items-center justify-center shadow-sm">
                <BarChart3 size={24} className="text-pink-500" />
              </div>
              <span className="text-[10px] font-bold text-gray-400 uppercase tracking-tight">
                Progresso
              </span>
            </button>
            <button
              onClick={() => setShowVehicles(true)}
              className="flex flex-col items-center gap-2"
            >
              <div className="w-14 h-14 bg-gray-50 rounded-2xl flex items-center justify-center text-indigo-500 shadow-sm">
                <Car size={24} />
              </div>
              <span className="text-[10px] font-bold text-gray-400 uppercase tracking-tight text-indigo-500 font-black">
                Veículos
              </span>
            </button>
          </div>
        </div>

        <div className="bg-white rounded-[32px] p-6 shadow-sm border border-gray-50">
          <div className="flex justify-between items-center mb-4">
            <span className="bg-blue-50 text-blue-600 text-[10px] font-black px-3 py-1 rounded-full uppercase tracking-wider">
              Último Instrutor
            </span>
            <div className="flex items-center gap-1 text-yellow-500 font-bold text-sm">
              <Star size={14} className="fill-current" /> 4.9
            </div>
          </div>
          <div className="flex items-center gap-4 mb-6">
            <img
              src={lastInstructor.photo}
              className="w-14 h-14 rounded-2xl object-cover"
              alt=""
            />
            <div>
              <h4 className="font-bold text-gray-800">{lastInstructor.name}</h4>
              <p className="text-xs text-gray-400 font-medium">
                {lastInstructor.distance} • {lastInstructor.car}
              </p>
            </div>
          </div>
          <button
            onClick={onStartSearch}
            className="w-full bg-[#0F172A] text-white font-bold py-4 rounded-2xl shadow-lg active:scale-95 transition-all"
          >
            Agendar Novamente
          </button>
        </div>
      </div>
    </div>
  );
};

export default Home;
