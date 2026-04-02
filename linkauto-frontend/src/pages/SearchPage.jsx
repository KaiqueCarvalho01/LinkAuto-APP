import React from "react";
import { ChevronLeft, MapPin, Star } from "lucide-react";

const SearchPage = ({
  searchTerm,
  setSearchTerm,
  instructors,
  onSelectInstructor,
  onBack,
}) => {
  return (
    <div className="flex flex-col min-h-screen bg-white">
      <header className="p-4 flex items-center gap-4 border-b sticky top-0 bg-white z-50">
        <button
          onClick={onBack}
          className="p-2 hover:bg-gray-100 rounded-full transition-colors"
        >
          <ChevronLeft size={24} />
        </button>
        <div className="relative flex-grow">
          <MapPin className="absolute left-3 top-3 text-blue-500" size={18} />
          <input
            autoFocus
            type="text"
            className="w-full bg-gray-50 border-none pl-10 pr-4 py-2.5 rounded-xl text-sm focus:ring-2 focus:ring-blue-500 outline-none"
            placeholder="Onde você está?"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </header>

      <main className="p-4 space-y-4">
        <h3 className="text-xs font-black text-gray-400 uppercase tracking-widest px-2">
          Instrutores disponíveis
        </h3>
        {instructors.map((instructor) => (
          <div
            key={instructor.id}
            onClick={() => onSelectInstructor(instructor)}
            className="bg-white p-4 rounded-3xl border border-gray-100 shadow-sm flex items-center gap-4 active:scale-[0.98] transition-all cursor-pointer"
          >
            <img
              src={instructor.photo}
              className="w-14 h-14 rounded-2xl object-cover"
              alt=""
            />
            <div className="flex-grow">
              <h4 className="font-bold text-gray-800">{instructor.name}</h4>
              <p className="text-[10px] text-gray-400 font-bold uppercase tracking-tighter">
                {instructor.neighborhood}
              </p>
              <p className="text-blue-600 font-black text-sm mt-1">
                R$ {instructor.price},00
              </p>
            </div>
            <div className="bg-yellow-50 px-2 py-1 rounded-lg flex items-center gap-1 text-yellow-600 font-bold text-xs">
              <Star size={12} className="fill-current" /> {instructor.rating}
            </div>
          </div>
        ))}
      </main>
    </div>
  );
};

export default SearchPage;
