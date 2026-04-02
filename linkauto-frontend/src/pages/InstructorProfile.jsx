import React, { useState } from "react";
import { ChevronLeft, ShieldCheck } from "lucide-react";
import ConfirmationModal from "../components/ConfirmationModal"; // Importando o novo modal

const InstructorProfile = ({ instructor, onBack, onConfirm }) => {
  const [selectedTime, setSelectedTime] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false); // Estado para controlar o Pop-up

  if (!instructor) return null;

  return (
    <div className="flex flex-col min-h-screen bg-white pb-24 font-sans text-gray-900">
      <header className="p-4 flex items-center gap-4 border-b sticky top-0 bg-white z-10">
        <button
          onClick={onBack}
          className="p-2 hover:bg-gray-100 rounded-full transition-colors"
        >
          <ChevronLeft size={24} />
        </button>
        <h2 className="font-bold text-lg">Perfil do Instrutor</h2>
      </header>

      <main className="p-6">
        <div className="flex flex-col items-center mb-8">
          <img
            src={instructor.photo}
            className="w-24 h-24 rounded-3xl shadow-lg mb-4 object-cover border-4 border-blue-50"
            alt=""
          />
          <h3 className="text-2xl font-bold">{instructor.name}</h3>
          <div className="flex items-center gap-2 mt-1 text-green-600 font-medium text-sm">
            <ShieldCheck size={18} /> Credenciado LinkAuto
          </div>
        </div>

        <div className="mb-8">
          <h4 className="font-bold text-gray-800 mb-4 flex justify-between items-center">
            Escolha um horário{" "}
            <span className="text-[10px] text-blue-500 font-bold">
              AULAS DE 50MIN
            </span>
          </h4>
          <div className="grid grid-cols-3 gap-2">
            {["08:00", "08:50", "09:40", "14:00", "14:50", "15:40"].map(
              (slot) => (
                <button
                  key={slot}
                  onClick={() => setSelectedTime(slot)}
                  className={`py-3 border rounded-xl text-sm font-bold transition-all ${
                    selectedTime === slot
                      ? "bg-blue-600 text-white border-blue-600 shadow-md"
                      : "bg-white text-gray-700 border-gray-200"
                  }`}
                >
                  {slot}
                </button>
              ),
            )}
          </div>
        </div>
      </main>

      <footer className="fixed bottom-0 w-full p-4 bg-white border-t flex items-center justify-between shadow-2xl">
        <div>
          <p className="text-[10px] text-gray-400 font-black uppercase tracking-widest">
            Total
          </p>
          <p className="text-xl font-black text-blue-600">
            R$ {instructor.price},00
          </p>
        </div>
        <button
          disabled={!selectedTime}
          onClick={() => setIsModalOpen(true)} // Em vez de confirmar direto, abre o modal
          className={`font-bold px-8 py-4 rounded-2xl shadow-lg transition-all ${
            selectedTime
              ? "bg-blue-600 text-white active:scale-95"
              : "bg-gray-200 text-gray-400 cursor-not-allowed"
          }`}
        >
          {selectedTime ? "Agendar" : "Escolha a hora"}
        </button>
      </footer>

      {/* Renderizando o Modal de Confirmação */}
      <ConfirmationModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onConfirm={() => onConfirm(selectedTime)} // Aqui sim dispara a função final do App.jsx
        instructorName={instructor.name}
        time={selectedTime}
      />
    </div>
  );
};

export default InstructorProfile;
