import React from "react";
import { AlertCircle } from "lucide-react";

const ConfirmationModal = ({
  isOpen,
  onClose,
  onConfirm,
  instructorName,
  time,
}) => {
  // Se o modal não estiver aberto, não renderiza nada
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div className="bg-white w-full max-w-sm rounded-3xl p-6 shadow-2xl animate-in zoom-in duration-200">
        <div className="flex flex-col items-center text-center">
          <div className="bg-blue-50 p-3 rounded-full mb-4">
            <AlertCircle className="text-blue-600" size={32} />
          </div>

          <h3 className="text-xl font-bold text-gray-900 mb-2">
            Confirmar Agendamento?
          </h3>

          <p className="text-sm text-gray-500 mb-6">
            Você está agendando uma aula de 50 minutos com{" "}
            <span className="font-bold text-gray-800">{instructorName}</span> às{" "}
            <span className="font-bold text-gray-800">{time}</span>.
          </p>

          <div className="flex flex-col w-full gap-3">
            <button
              onClick={onConfirm}
              className="w-full bg-blue-600 text-white font-bold py-4 rounded-2xl shadow-lg active:scale-95 transition-all"
            >
              Sim, confirmar
            </button>

            <button
              onClick={onClose}
              className="w-full bg-gray-100 text-gray-600 font-bold py-4 rounded-2xl active:scale-95 transition-all"
            >
              Não, voltar
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ConfirmationModal;
