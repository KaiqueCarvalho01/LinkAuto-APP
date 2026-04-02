import React from "react";
import { Clock, Calendar, MapPin, CheckCircle } from "lucide-react";

const MyLessons = ({ lessons }) => {
  return (
    <main className="p-4">
      <header className="mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Minhas Aulas</h2>
        <p className="text-sm text-gray-500 font-medium">
          Controlo das suas sessões de 50 minutos
        </p>
      </header>

      <div className="space-y-4">
        {lessons.length === 0 ? (
          <div className="text-center py-10 bg-white rounded-2xl border border-dashed border-gray-300">
            <p className="text-gray-400 text-sm">
              Ainda não agendou nenhuma aula.
            </p>
          </div>
        ) : (
          lessons.map((lesson) => (
            <div
              key={lesson.id}
              className="bg-white p-4 rounded-2xl shadow-sm border border-gray-100"
            >
              <div className="flex justify-between items-start mb-3">
                <div className="flex items-center gap-3">
                  <div className="bg-blue-100 p-2 rounded-lg text-blue-600">
                    <Calendar size={20} />
                  </div>
                  <div>
                    <h4 className="font-bold text-gray-800">
                      {lesson.instructorName}
                    </h4>
                    <p className="text-[10px] text-gray-400 font-bold uppercase tracking-widest">
                      {lesson.date}
                    </p>
                  </div>
                </div>
                {/* Etiqueta de status da aula */}
                <span
                  className={`text-[10px] font-black px-2 py-1 rounded-md uppercase ${
                    lesson.status === "scheduled"
                      ? "bg-blue-50 text-blue-600"
                      : "bg-green-50 text-green-600"
                  }`}
                >
                  {lesson.status === "scheduled" ? "Agendada" : "Concluída"}
                </span>
              </div>

              <div className="flex items-center justify-between text-sm text-gray-500 border-t pt-3">
                <div className="flex items-center gap-1">
                  <Clock size={14} className="text-blue-500" />
                  <span className="font-medium text-gray-700">
                    {lesson.time}
                  </span>
                  <span className="text-[10px]">(50 min)</span>
                </div>
                <div className="flex items-center gap-1">
                  <MapPin size={14} />
                  <span>{lesson.neighborhood}</span>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </main>
  );
};

export default MyLessons;
