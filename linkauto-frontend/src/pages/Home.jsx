import React, { useState, useMemo } from "react";
import { Search, MapPin, Star } from "lucide-react";
import InstructorCard from "../components/InstructorCard";

const Home = ({
  searchTerm,
  setSearchTerm,
  showResults,
  setShowResults,
  instructors,
  onSelectInstructor,
}) => {
  const [activeFilter, setActiveFilter] = useState("Todos");

  // Logica de filtragem e ordenacao
  const filteredInstructors = useMemo(() => {
    let list = [...instructors];
    if (activeFilter === "Mais Baratos") {
      list.sort((a, b) => a.price - b.price);
    } else if (activeFilter === "Melhores Notas") {
      list.sort((a, b) => b.rating - a.rating);
    }
    return list;
  }, [activeFilter, instructors]);

  const handleSearch = () => {
    if (searchTerm.trim() !== "") setShowResults(true);
  };

  return (
    <main className="p-4">
      {!showResults && (
        <div className="mt-6 mb-8 text-center">
          <h2 className="text-2xl font-bold text-gray-800 mb-2">
            Encontre seu instrutor
          </h2>
          <p className="text-gray-500 mb-6 italic text-sm">
            Aulas avulsas de 50 minutos em Mogi Mirim.
          </p>
        </div>
      )}

      <div className="relative mb-6">
        <MapPin className="absolute left-4 top-4 text-blue-500" size={20} />
        <input
          type="text"
          className="w-full border-none pl-12 pr-4 py-4 rounded-2xl shadow-md focus:ring-2 focus:ring-blue-500 text-gray-700 bg-white"
          placeholder="Digite seu bairro..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
        <button
          onClick={handleSearch}
          className="mt-3 w-full bg-blue-600 text-white font-bold py-4 rounded-2xl shadow-lg active:scale-95"
        >
          Buscar Agora
        </button>
      </div>

      {showResults && (
        <div className="space-y-4">
          <div className="flex gap-2 overflow-x-auto pb-2 no-scrollbar">
            {["Todos", "Mais Baratos", "Melhores Notas"].map((filter) => (
              <button
                key={filter}
                onClick={() => setActiveFilter(filter)}
                className={`whitespace-nowrap px-4 py-2 rounded-full text-xs font-bold border transition-colors ${
                  activeFilter === filter
                    ? "bg-blue-600 text-white border-blue-600"
                    : "bg-white text-gray-500 border-gray-100 shadow-sm"
                }`}
              >
                {filter}
              </button>
            ))}
          </div>

          <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-widest pt-2">
            Resultados
          </h3>
          {filteredInstructors.map((instructor) => (
            <InstructorCard
              key={instructor.id}
              instructor={instructor}
              onSelect={onSelectInstructor}
            />
          ))}
        </div>
      )}
    </main>
  );
};

export default Home;
