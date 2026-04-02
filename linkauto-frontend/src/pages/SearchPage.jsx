import React, { useState } from "react";
import { ChevronLeft, MapPin, Star, SlidersHorizontal, CircleDollarSign, GraduationCap } from "lucide-react";

const SearchPage = ({ searchTerm, setSearchTerm, instructors, onSelectInstructor, onBack }) => {
  const [activeFilter, setActiveFilter] = useState("Proximidade");

  // Captura o "Enter" no teclado
  const handleSearchSubmit = (e) => {
    e.preventDefault();
    // A lógica de filtragem já acontece pelo filtro no map abaixo
  };

  // RF02 - Filtros: avaliação média, preço por hora, disponibilidade 
  const filteredInstructors = instructors.filter((inst) =>
    inst.neighborhood.toLowerCase().includes(searchTerm.toLowerCase()) ||
    inst.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const filters = [
    { id: "geo", label: "Proximidade", icon: <MapPin size={14} /> },
    { id: "price", label: "Preço", icon: <CircleDollarSign size={14} /> },
    { id: "rating", label: "Avaliação", icon: <Star size={14} /> },
    { id: "spec", label: "Especialidade", icon: <GraduationCap size={14} /> },
  ];

  return (
    <div className="flex flex-col min-h-screen bg-white">
      {/* Header com Form para funcionar o Enter */}
      <header className="p-4 border-b sticky top-0 bg-white z-50">
        <div className="flex items-center gap-4 mb-4">
          <button onClick={onBack} className="p-2 hover:bg-gray-100 rounded-full">
            <ChevronLeft size={24} />
          </button>
          
          <form onSubmit={handleSearchSubmit} className="relative flex-grow">
            <MapPin className="absolute left-3 top-3 text-blue-500" size={18} />
            <input
              autoFocus
              type="text"
              className="w-full bg-gray-50 border-none pl-10 pr-4 py-2.5 rounded-xl text-sm focus:ring-2 focus:ring-blue-500 outline-none"
              placeholder="Bairro ou nome do instrutor"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </form>
        </div>

        {/* Barra de Filtros - RF02  */}
        <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
          <button className="p-2.5 bg-gray-100 rounded-xl text-gray-600">
            <SlidersHorizontal size={18} />
          </button>
          {filters.map((f) => (
            <button
              key={f.id}
              onClick={() => setActiveFilter(f.label)}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold whitespace-nowrap transition-all ${
                activeFilter === f.label 
                ? "bg-blue-600 text-white shadow-md shadow-blue-200" 
                : "bg-gray-50 text-gray-500 border border-gray-100"
              }`}
            >
              {f.icon}
              {f.label}
            </button>
          ))}
        </div>
      </header>

      <main className="p-4 space-y-4">
        <div className="flex justify-between items-center px-2">
          <h3 className="text-[10px] font-black text-gray-400 uppercase tracking-widest">
            {filteredInstructors.length} Instrutores encontrados
          </h3>
        </div>

        {filteredInstructors.length > 0 ? (
          filteredInstructors.map((instructor) => (
            <div 
              key={instructor.id} 
              onClick={() => onSelectInstructor(instructor)}
              className="bg-white p-4 rounded-[32px] border border-gray-100 shadow-sm flex items-center gap-4 active:scale-[0.98] transition-all cursor-pointer"
            >
              <div className="relative">
                <img src={instructor.photo} className="w-16 h-16 rounded-2xl object-cover" alt="" />
                <div className="absolute -top-2 -right-2 bg-green-500 w-4 h-4 border-2 border-white rounded-full"></div>
              </div>
              
              <div className="flex-grow">
                <h4 className="font-bold text-gray-800">{instructor.name}</h4>
                <p className="text-[10px] text-gray-400 font-bold uppercase tracking-tight">{instructor.neighborhood}</p>
                <div className="flex items-center gap-3 mt-2">
                  <span className="text-blue-600 font-black text-sm">R$ {instructor.price}/h</span>
                  <span className="text-gray-300 text-xs">|</span>
                  <div className="flex items-center gap-1 text-yellow-500 font-bold text-xs">
                    <Star size={12} className="fill-current" /> {instructor.rating}
                  </div>
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="text-center py-20">
            <p className="text-gray-400 font-medium">Nenhum instrutor encontrado nesta região.</p>
          </div>
        )}
      </main>
    </div>
  );
};

export default SearchPage;