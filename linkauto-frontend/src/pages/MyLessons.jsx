import React from "react";
import { Calendar, Clock, MapPin, ChevronRight } from "lucide-react";

const MyLessons = ({ lessons, onSelectLesson }) => {
  return (
    <main className="p-4 pb-24 bg-[#F8F9FC] min-h-screen">
      <header className="mb-6">
        <h2 className="text-2xl font-bold text-gray-800 tracking-tight">Minhas Aulas</h2>
        <p className="text-xs text-gray-400 font-medium">Toque em uma aula para ver detalhes e mensagens</p>
      </header>

      <div className="space-y-4">
        {lessons.length > 0 ? (
          lessons.map((lesson) => (
            <div 
              key={lesson.id} 
              onClick={() => onSelectLesson(lesson)}
              className="bg-white p-5 rounded-[32px] border border-gray-100 shadow-sm shadow-blue-900/5 flex items-center gap-4 active:scale-[0.98] transition-all cursor-pointer"
            >
              <div className="w-12 h-12 bg-blue-50 rounded-2xl flex items-center justify-center text-blue-600 font-bold text-lg">
                {lesson.instructorName[0]}
              </div>

              <div className="flex-grow">
                <div className="flex justify-between items-start">
                  <h4 className="font-bold text-gray-800 text-sm">{lesson.instructorName}</h4>
                  <span className={`text-[8px] font-black px-2 py-0.5 rounded-full uppercase tracking-wider ${
                    lesson.status === 'completed' ? 'bg-green-50 text-green-600' : 'bg-blue-50 text-blue-600'
                  }`}>
                    {lesson.status === 'completed' ? 'Realizada' : 'Agendada'}
                  </span>
                </div>
                
                <div className="flex items-center gap-3 mt-2 text-[10px] text-gray-400 font-bold uppercase tracking-tight">
                  <div className="flex items-center gap-1">
                    <Calendar size={12} className="text-blue-500" /> {lesson.date}
                  </div>
                  <div className="flex items-center gap-1">
                    <Clock size={12} className="text-blue-500" /> {lesson.time}
                  </div>
                </div>
              </div>

              <ChevronRight size={18} className="text-gray-300" />
            </div>
          ))
        ) : (
          <div className="text-center py-20">
            <p className="text-gray-400 font-medium">Você ainda não tem aulas agendadas.</p>
          </div>
        )}
      </div>
    </main>
  );
};

export default MyLessons;