import React, { useState } from "react";
import { Clock, Calendar, MapPin, Star } from "lucide-react";
import RatingModal from "../components/RatingModal";

const MyLessons = ({ lessons }) => {
  const [selectedLesson, setSelectedLesson] = useState(null);

  const handleRatingSubmit = (rating, comment) => {
    // Aqui no futuro enviamos para o backend (RF06)
    console.log(
      `Avaliação para ${selectedLesson.instructorName}: ${rating} estrelas. Comentário: ${comment}`,
    );
    alert("Obrigado pela sua avaliação!");
    setSelectedLesson(null);
  };

  return (
    <main className="p-4 pb-24">
      <header className="mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Minha Agenda</h2>
      </header>

      <div className="space-y-4">
        {lessons.map((lesson) => (
          <div
            key={lesson.id}
            className="bg-white p-4 rounded-2xl border border-gray-100 shadow-sm"
          >
            <div className="flex justify-between items-start mb-4">
              <div className="flex items-center gap-3">
                <div
                  className={`p-2 rounded-lg ${lesson.status === "completed" ? "bg-green-50 text-green-600" : "bg-blue-50 text-blue-600"}`}
                >
                  <Calendar size={20} />
                </div>
                <div>
                  <h4 className="font-bold text-gray-800">
                    {lesson.instructorName}
                  </h4>
                  <p className="text-[10px] text-gray-400 font-bold uppercase">
                    {lesson.date}
                  </p>
                </div>
              </div>
              <span
                className={`text-[10px] font-black px-2 py-1 rounded-md ${
                  lesson.status === "completed"
                    ? "bg-green-100 text-green-600"
                    : "bg-blue-100 text-blue-600"
                }`}
              >
                {lesson.status === "completed" ? "Realizada" : "Agendada"}
              </span>
            </div>

            <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
              <div className="flex items-center gap-1 font-medium">
                <Clock size={14} className="text-blue-500" /> {lesson.time}
              </div>
              <div className="flex items-center gap-1">
                <MapPin size={14} /> {lesson.neighborhood}
              </div>
            </div>

            {/* Botao de avaliacao liberado apenas para aulas realizadas (RN05) */}
            {lesson.status === "completed" && (
              <button
                onClick={() => setSelectedLesson(lesson)}
                className="w-full py-3 bg-yellow-50 text-yellow-700 rounded-xl text-xs font-bold flex items-center justify-center gap-2 active:scale-95 transition-all"
              >
                <Star size={14} className="fill-current" /> Avaliar Experiência
              </button>
            )}
          </div>
        ))}
      </div>

      <RatingModal
        isOpen={!!selectedLesson}
        targetName={selectedLesson?.instructorName}
        onClose={() => setSelectedLesson(null)}
        onSubmit={handleRatingSubmit}
      />
    </main>
  );
};

export default MyLessons;
