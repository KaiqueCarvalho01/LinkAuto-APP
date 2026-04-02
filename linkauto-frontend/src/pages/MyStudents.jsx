import React from "react";
import { ChevronLeft, User, MessageCircle, Calendar } from "lucide-react";

const MyStudents = ({ students, onBack, onSelectStudent }) => {
  return (
    <div className="flex flex-col min-h-screen bg-[#F8F9FC] font-sans pb-10">
      <header className="p-6 flex items-center gap-4 bg-white border-b border-gray-100">
        <button onClick={onBack} className="p-2 hover:bg-gray-50 rounded-full transition-all">
          <ChevronLeft size={24} className="text-gray-800" />
        </button>
        <h2 className="text-xl font-bold text-gray-800 italic">Meus Alunos</h2>
      </header>

      <main className="p-5 space-y-4">
        {students.length > 0 ? (
          students.map((student) => (
            <div 
              key={student.id}
              className="bg-white p-5 rounded-[32px] border border-gray-100 shadow-sm flex items-center gap-4"
            >
              <div className="w-14 h-14 bg-blue-50 rounded-2xl flex items-center justify-center text-blue-600 font-black text-xl">
                {student.name[0]}
              </div>
              
              <div className="flex-grow">
                <h4 className="font-bold text-gray-800 text-base">{student.name}</h4>
                <div className="flex items-center gap-3 mt-1">
                  <div className="flex items-center gap-1 text-[10px] text-gray-400 font-bold uppercase">
                    <Calendar size={12} className="text-blue-500" /> {student.totalLessons} Aulas
                  </div>
                  <span className="text-gray-200">|</span>
                  <div className="flex items-center gap-1 text-[10px] text-gray-400 font-bold uppercase">
                    <MessageCircle size={12} className="text-green-500" /> Ativo
                  </div>
                </div>
              </div>

              <button 
                onClick={() => onSelectStudent(student)}
                className="p-3 bg-gray-50 text-gray-400 rounded-2xl hover:text-blue-600 hover:bg-blue-50 transition-all"
              >
                <ChevronLeft size={20} className="rotate-180" />
              </button>
            </div>
          ))
        ) : (
          <div className="text-center py-20">
            <p className="text-gray-400 font-medium">Você ainda não possui alunos vinculados.</p>
          </div>
        )}
      </main>
    </div>
  );
};

export default MyStudents;