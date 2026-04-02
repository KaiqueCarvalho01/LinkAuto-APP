import React from "react";
import { Star, MapPin } from "lucide-react";

// Componente para exibir o card individual do instrutor
const InstructorCard = ({ instructor, onSelect }) => {
  return (
    <div className="bg-white p-4 rounded-2xl shadow-sm border border-gray-100 flex items-center gap-4 active:bg-gray-50 transition-colors">
      <img
        src={instructor.photo}
        alt={instructor.name}
        className="w-16 h-16 rounded-xl object-cover border-2 border-blue-50"
      />

      <div className="flex-grow">
        <div className="flex justify-between items-start">
          <h4 className="font-bold text-gray-800">{instructor.name}</h4>
          <span className="flex items-center text-xs font-bold bg-yellow-100 text-yellow-700 px-2 py-1 rounded-lg">
            <Star size={12} className="fill-current mr-1" /> {instructor.rating}
          </span>
        </div>

        <p className="text-sm text-gray-500 flex items-center mt-1">
          <MapPin size={14} className="mr-1" /> {instructor.neighborhood}
        </p>

        <div className="flex items-center mt-2 justify-between">
          <span className="text-blue-600 font-bold text-lg">
            R$ {instructor.price}
            <span className="text-[10px] text-gray-400 font-normal">
              /50min
            </span>
          </span>

          <button
            onClick={() => onSelect(instructor)}
            className="bg-blue-50 text-blue-600 text-xs font-bold px-4 py-2 rounded-lg hover:bg-blue-600 hover:text-white transition-all"
          >
            Ver Agenda
          </button>
        </div>
      </div>
    </div>
  );
};

export default InstructorCard;
