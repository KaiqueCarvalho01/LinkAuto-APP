import React, { useState } from "react";
import { ChevronLeft, Calendar, Clock, Send, MessageSquare } from "lucide-react";

const LessonDetails = ({ lesson, onBack }) => {
  const [newMessage, setNewMessage] = useState("");
  const [chat, setChat] = useState([
    { id: 1, sender: "system", text: "Agendamento realizado com sucesso!", time: "10:00" }
  ]);

  const handleSendMessage = (e) => {
    e.preventDefault();
    if (newMessage.trim()) {
      const msg = {
        id: Date.now(),
        sender: "me",
        text: newMessage,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setChat([...chat, msg]);
      setNewMessage("");
    }
  };

  return (
    <div className="flex flex-col min-h-screen bg-[#F8F9FC] font-sans">
      {/* Cabeçalho Ajustado - Mesma altura do perfil */}
      <div className="bg-gradient-to-b from-[#2563EB] to-[#3B82F6] pt-8 pb-16 px-6 rounded-b-[32px] relative">
        <button onClick={onBack} className="p-2 bg-white/20 backdrop-blur-md rounded-full text-white mb-2">
          <ChevronLeft size={20} />
        </button>
        
        <div className="flex flex-col items-center text-white">
          <h2 className="text-xl font-bold italic tracking-tight">Detalhes da Aula</h2>
          <p className="text-blue-100 text-[10px] font-bold uppercase tracking-widest mt-1">Combine o local com seu instrutor</p>
        </div>
      </div>

      {/* Card de Informações - Estilo Perfil Instrutor */}
      <div className="px-5 -mt-8 relative z-10">
        <div className="bg-white rounded-[24px] p-5 shadow-xl shadow-blue-900/5 mb-6 border border-gray-50">
          <div className="flex items-center gap-4 mb-4">
            <div className="w-12 h-12 bg-blue-50 rounded-2xl flex items-center justify-center text-blue-600 font-black text-lg">
              {lesson.instructorName[0]}
            </div>
            <div className="flex-grow">
              <h3 className="font-bold text-gray-800 text-base">{lesson.instructorName}</h3>
              <span className="bg-blue-50 text-blue-600 text-[9px] font-black px-2 py-0.5 rounded-md uppercase tracking-wider">
                {lesson.status === 'scheduled' ? 'Agendada' : 'Realizada'}
              </span>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-50">
            <div className="flex items-center gap-2 text-gray-400">
              <Calendar size={14} className="text-blue-500" />
              <span className="text-[11px] font-bold">{lesson.date}</span>
            </div>
            <div className="flex items-center gap-2 text-gray-400">
              <Clock size={14} className="text-blue-500" />
              <span className="text-[11px] font-bold">{lesson.time}h</span>
            </div>
          </div>
        </div>

        {/* Chat / Mensagens */}
        <section className="flex flex-col h-[380px] px-1">
          <div className="flex items-center gap-2 mb-4">
            <MessageSquare size={16} className="text-gray-400" />
            <h4 className="font-bold text-gray-800 text-sm italic">Mensagens</h4>
          </div>

          <div className="flex-grow overflow-y-auto space-y-4 mb-4 pr-1 scrollbar-hide">
            {chat.map((msg) => (
              <div key={msg.id} className={`flex ${msg.sender === 'me' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[85%] p-3.5 rounded-[20px] text-xs font-medium shadow-sm ${
                  msg.sender === 'me' 
                  ? 'bg-blue-600 text-white rounded-tr-none' 
                  : 'bg-white text-gray-600 rounded-tl-none border border-gray-50'
                }`}>
                  {msg.text}
                  <p className={`text-[8px] mt-1.5 opacity-60 font-bold ${msg.sender === 'me' ? 'text-right' : 'text-left'}`}>
                    {msg.time}
                  </p>
                </div>
              </div>
            ))}
          </div>

          {/* Input de Mensagem */}
          <form onSubmit={handleSendMessage} className="relative pb-4">
            <input
              type="text"
              className="w-full bg-white border border-gray-100 pl-5 pr-14 py-4 rounded-[20px] text-xs shadow-sm focus:ring-2 focus:ring-blue-500 outline-none transition-all placeholder:text-gray-300"
              placeholder="Digite o local de encontro..."
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
            />
            <button 
              type="submit"
              className="absolute right-2 top-2 bg-[#0F172A] text-white p-2.5 rounded-xl shadow-md active:scale-90 transition-all"
            >
              <Send size={16} />
            </button>
          </form>
        </section>
      </div>
    </div>
  );
};

export default LessonDetails;