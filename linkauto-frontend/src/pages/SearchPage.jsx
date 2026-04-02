import React, { useState, useMemo } from "react";
import { ChevronLeft, MapPin, Star, SlidersHorizontal, CircleDollarSign, GraduationCap } from "lucide-react";

const SearchPage = ({ searchTerm, setSearchTerm, instructors, onSelectInstructor, onBack }) => {
  const [activeFilter, setActiveFilter] = useState("Proximidade");

  const filters = [
    { id: "geo", label: "Proximidade", icon: <MapPin size={14} /> },
    { id: "price", label: "Preço", icon: <CircleDollarSign size={14} /> },
    { id: "rating", label: "Avaliação", icon: <Star size={14} /> },
  ];

  // Lógica de Filtragem e Ordenação Combinada
  const filteredAndSortedInstructors = useMemo(() => {
    let result = instructors.filter((inst) =>
      inst.neighborhood.toLowerCase().includes(searchTerm.toLowerCase()) ||
      inst.name.toLowerCase().includes(searchTerm.toLowerCase())
    );

    if (activeFilter === "Preço") {
      result = [...result].sort((a, b) => a.price - b.price); // Do mais barato ao mais caro
    } else if (activeFilter === "Avaliação") {
      result = [...result].sort((a, b) => b.rating - a.rating); // Melhor nota primeiro
    }

    return result;
  }, [searchTerm, instructors, activeFilter]);

  return (
    <div className="flex flex-col min-h-screen bg-white font-sans">
      <header className="p-4 border-b sticky top-0 bg-white z-50">
        <div className="flex items-center gap-4 mb-4">
          <button onClick={onBack} className="p-2 hover:bg-gray-100 rounded-full transition-colors">
            <ChevronLeft size={24} />
          </button>
          
          <form onSubmit={(e) => e.preventDefault()} className="relative flex-grow">
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

        <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
          <button className="p-2.5 bg-gray-100 rounded-xl text-gray-600">
            <SlidersHorizontal size={18} />
          </button>
          {filters.map((f) => (
            <button
              key={f.id}
              onClick={() => setActiveFilter(f.label)}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-[10px] font-black uppercase tracking-wider whitespace-nowrap transition-all ${
                activeFilter === f.label 
                ? "bg-blue-600 text-white shadow-md shadow-blue-100" 
                : "bg-white text-gray-400 border border-gray-100"
              }`}
            >
              {f.icon}
              {f.label}
            </button>
          ))}
        </div>
      </header>

      <main className="p-4 space-y-4">
        <div className="px-2">
          <h3 className="text-[9px] font-black text-gray-300 uppercase tracking-[0.2em]">
            {filteredAndSortedInstructors.length} Resultados para "{searchTerm || 'Todos'}"
          </h3>
        </div>

        {filteredAndSortedInstructors.length > 0 ? (
          filteredAndSortedInstructors.map((instructor) => (
            <div 
              key={instructor.id} 
              onClick={() => onSelectInstructor(instructor)}
              className="bg-white p-4 rounded-[32px] border border-gray-100 shadow-sm flex items-center gap-4 active:scale-[0.97] transition-all cursor-pointer hover:border-blue-100"
            >
              <div className="relative">
                <img src={instructor.photo} className="w-16 h-16 rounded-2xl object-cover border border-gray-50" alt="" />
                <div className="absolute -top-1 -right-1 bg-green-500 w-3.5 h-3.5 border-2 border-white rounded-full"></div>
              </div>
              
              <div className="flex-grow">
                <h4 className="font-bold text-gray-800 text-sm leading-tight">{instructor.name}</h4>
                <p className="text-[9px] text-gray-400 font-black uppercase tracking-tight mt-0.5">{instructor.neighborhood}</p>
                
                <div className="flex items-center gap-3 mt-2.5">
                  <span className="text-blue-600 font-black text-xs tracking-tighter">R$ {instructor.price}/h</span>
                  <span className="text-gray-100 text-xs">|</span>
                  <div className="flex items-center gap-1 text-yellow-500 font-bold text-[11px]">
                    <Star size={10} className="fill-current" /> {instructor.rating}
                  </div>
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="text-center py-24 px-10">
            <div className="w-16 h-16 bg-gray-50 rounded-full flex items-center justify-center mx-auto mb-4">
              <MapPin size={24} className="text-gray-200" />
            </div>
            <p className="text-gray-400 font-bold text-sm">Nenhum instrutor encontrado.</p>
            <p className="text-gray-300 text-xs mt-1">Tente buscar por Centro ou Mogi Mirim.</p>
          </div>
        )}
      </main>
    </div>
  );
};

export default SearchPage;