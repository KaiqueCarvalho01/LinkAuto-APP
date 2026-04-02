import React from "react";
import { Calendar, Clock, ChevronRight, User } from "lucide-react";

const MyLessons = ({ lessons, onSelectLesson, isInstructor = false }) => {
  
  // Função auxiliar para definir o texto e a cor da tag de status
  const getStatusDetails = (status) => {
    switch (status) {
      case 'completed':
        return { label: 'Realizada', class: 'bg-green-50 text-green-600' };
      case 'confirmed':
        return { label: 'Confirmada', class: 'bg-blue-50 text-blue-600' };
      case 'scheduled':
        return { label: 'Pendente', class: 'bg-orange-50 text-orange-600' };
      default:
        return { label: 'Agendada', class: 'bg-gray-50 text-gray-600' };
    }
  };

  return (
    <main className="p-4 pb-24 bg-[#F8F9FC] min-h-screen">
      <header className="mb-6 px-2">
        <h2 className="text-2xl font-bold text-gray-800 tracking-tight">
          {isInstructor ? "Minha Agenda" : "Minhas Aulas"}
        </h2>
        <p className="text-xs text-gray-400 font-medium">
          {isInstructor ? "Gerencie suas aulas confirmadas" : "Toque para ver detalhes e mensagens"}
        </p>
      </header>

      <div className="space-y-4">
        {lessons.length > 0 ? (
          lessons.map((lesson) => {
            const status = getStatusDetails(lesson.status);
            return (
              <div 
                key={lesson.id} 
                onClick={() => onSelectLesson(lesson)}
                className="bg-white p-5 rounded-[32px] border border-gray-100 shadow-sm shadow-blue-900/5 flex items-center gap-4 active:scale-[0.98] transition-all cursor-pointer"
              >
                <div className="w-12 h-12 bg-slate-50 rounded-2xl flex items-center justify-center text-slate-400">
                  <User size={24} />
                </div>

                <div className="flex-grow">
                  <div className="flex justify-between items-start">
                    <h4 className="font-bold text-gray-800 text-sm">
                      {isInstructor ? `Aluno: ${lesson.studentName}` : lesson.instructorName}
                    </h4>
                    {/* TAG DINÂMICA AQUI */}
                    <span className={`text-[8px] font-black px-2 py-0.5 rounded-full uppercase tracking-wider ${status.class}`}>
                      {status.label}
                    </span>
                  </div>
                  
                  <div className="flex items-center gap-3 mt-2 text-[10px] text-gray-400 font-bold uppercase tracking-tight">
                    <div className="flex items-center gap-1">
                      <Calendar size={12} className="text-blue-500" /> {lesson.date}
                    </div>
                    <div className="flex items-center gap-1">
                      <Clock size={12} className="text-blue-500" /> {lesson.time}h
                    </div>
                  </div>
                </div>

                <ChevronRight size={18} className="text-gray-300" />
              </div>
            );
          })
        ) : (
          <div className="text-center py-20 bg-white rounded-[32px] border border-dashed border-gray-200 mx-2">
            <p className="text-gray-400 text-xs font-medium">Nenhuma aula na lista.</p>
          </div>
        )}
      </div>
    </main>
  );
};

export default MyLessons;