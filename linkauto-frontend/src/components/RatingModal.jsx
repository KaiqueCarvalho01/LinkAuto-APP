import React, { useState } from "react";
import { Star, Send } from "lucide-react";

const RatingModal = ({ isOpen, onClose, onSubmit, targetName }) => {
  const [rating, setRating] = useState(0);
  const [comment, setComment] = useState("");

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div className="bg-white w-full max-w-sm rounded-3xl p-6 shadow-2xl animate-in zoom-in duration-200">
        <div className="text-center">
          <h3 className="text-xl font-bold text-gray-900 mb-1">Avaliar Aula</h3>
          <p className="text-sm text-gray-500 mb-6">
            Como foi sua experiência com {targetName}?
          </p>

          {/* Seleção de Estrelas */}
          <div className="flex justify-center gap-2 mb-6">
            {[1, 2, 3, 4, 5].map((star) => (
              <button
                key={star}
                onClick={() => setRating(star)}
                className="transition-transform active:scale-125"
              >
                <Star
                  size={32}
                  className={`${rating >= star ? "fill-yellow-400 text-yellow-400" : "text-gray-200"}`}
                />
              </button>
            ))}
          </div>

          <textarea
            className="w-full p-4 bg-gray-50 border-none rounded-2xl text-sm text-gray-700 focus:ring-2 focus:ring-blue-500 mb-6"
            placeholder="Deixe um comentário (opcional)..."
            rows="3"
            value={comment}
            onChange={(e) => setComment(e.target.value)}
          />

          <div className="flex flex-col gap-3">
            <button
              disabled={rating === 0}
              onClick={() => onSubmit(rating, comment)}
              className={`w-full font-bold py-4 rounded-2xl flex items-center justify-center gap-2 transition-all ${
                rating > 0
                  ? "bg-blue-600 text-white shadow-lg active:scale-95"
                  : "bg-gray-200 text-gray-400"
              }`}
            >
              Enviar Avaliação <Send size={18} />
            </button>
            <button
              onClick={onClose}
              className="text-sm text-gray-400 font-bold py-2"
            >
              Pular
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RatingModal;
