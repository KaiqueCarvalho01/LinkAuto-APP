import React from "react";
import { Star, Users, Calendar, CheckCircle, Clock } from "lucide-react";

const InstructorDashboard = ({ instructorData }) => {
  // Dados simulados de aulas do instrutor (RF07/RF08)
  const incomingLessons = [
    {
      id: 1,
      student: "Carlos Alberto",
      time: "08:00",
      status: "scheduled",
      type: "Habilitando",
    },
    {
      id: 2,
      student: "Julia Mendes",
      time: "10:30",
      status: "completed",
      type: "Reforço",
    },
  ];

  return (
    <main className="p-4 bg-gray-50 min-h-screen pb-24">
      <header className="mb-6">
        <p className="text-sm text-gray-500">Painel do Instrutor</p>
        <h2 className="text-2xl font-bold text-gray-800">
          {instructorData.name}
        </h2>
      </header>

      {/* Metricas de Desempenho (RF08) */}
      <div className="grid grid-cols-2 gap-4 mb-8">
        <div className="bg-white p-4 rounded-2xl border border-gray-100 shadow-sm">
          <Star className="text-yellow-500 mb-2" size={20} />
          <p className="text-2xl font-black">{instructorData.rating}</p>
          <p className="text-[10px] text-gray-400 font-bold uppercase">
            Avaliação Média
          </p>
        </div>
        <div className="bg-white p-4 rounded-2xl border border-gray-100 shadow-sm">
          <Users className="text-blue-500 mb-2" size={20} />
          <p className="text-2xl font-black">12</p>
          <p className="text-[10px] text-gray-400 font-bold uppercase">
            Total Alunos
          </p>
        </div>
      </div>

      {/* Gestao de Agenda (RF04/RF08) */}
      <section>
        <h3 className="font-bold text-gray-800 mb-4 flex justify-between items-center">
          Próximas Aulas
          <button className="text-blue-600 text-xs font-bold">Ver tudo</button>
        </h3>

        <div className="space-y-3">
          {incomingLessons.map((lesson) => (
            <div
              key={lesson.id}
              className="bg-white p-4 rounded-2xl flex items-center justify-between border border-gray-100"
            >
              <div className="flex items-center gap-3">
                <div className="bg-blue-50 w-10 h-10 rounded-xl flex items-center justify-center font-bold text-blue-600">
                  {lesson.student[0]}
                </div>
                <div>
                  <h4 className="font-bold text-sm">{lesson.student}</h4>
                  <p className="text-[10px] text-gray-400 font-medium">
                    {lesson.type}
                  </p>
                </div>
              </div>
              <div className="text-right">
                <p className="font-black text-blue-600 text-sm">
                  {lesson.time}
                </p>
                <span
                  className={`text-[8px] font-bold px-1.5 py-0.5 rounded uppercase ${
                    lesson.status === "completed"
                      ? "bg-green-100 text-green-600"
                      : "bg-blue-100 text-blue-600"
                  }`}
                >
                  {lesson.status === "completed" ? "Realizada" : "Pendente"}
                </span>
              </div>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
};

export default InstructorDashboard;
