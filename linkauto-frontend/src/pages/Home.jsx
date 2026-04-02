import React from "react";
import {
  Search,
  Calendar,
  Zap,
  BarChart3,
  Car,
  Bell,
  Star,
  MapPin,
} from "lucide-react";

const Home = ({ onStartSearch }) => {
  const lastInstructor = {
    name: "Marcos Silva",
    distance: "5 min de você",
    car: "HB20 Manual",
    rating: 4.9,
    photo: "https://i.pravatar.cc/150?u=marcos",
  };

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
            {["Agora", "Progresso", "Veículos"].map((label, idx) => (
              <button
                key={label}
                className="flex flex-col items-center gap-2 opacity-50"
              >
                <div className="w-14 h-14 bg-gray-50 rounded-2xl flex items-center justify-center shadow-sm">
                  {idx === 0 ? (
                    <Zap size={24} className="text-orange-500" />
                  ) : idx === 1 ? (
                    <BarChart3 size={24} className="text-pink-500" />
                  ) : (
                    <Car size={24} className="text-indigo-500" />
                  )}
                </div>
                <span className="text-[10px] font-bold text-gray-400 uppercase tracking-tight">
                  {label}
                </span>
              </button>
            ))}
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
